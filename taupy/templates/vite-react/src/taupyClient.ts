export type TaupyMessage = { type: string; [key: string]: any };

type Listener = (msg: TaupyMessage) => void;
type StatusListener = (status: "connecting" | "open" | "closed") => void;

export interface TaupyClientOptions {
  wsUrl?: string;
  autoReconnect?: boolean;
  reconnectDelayMs?: number;
  debug?: boolean;
}

export class TaupyClient {
  private ws: WebSocket | null = null;
  private listeners: Map<string, Set<Listener>> = new Map();
  private statusListeners: Set<StatusListener> = new Set();
  private opts: Required<TaupyClientOptions>;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(options: TaupyClientOptions = {}) {
    const hostname = typeof window !== "undefined" ? window.location.hostname : "localhost";
    this.opts = {
      wsUrl: options.wsUrl || `ws://${hostname}:8765`,
      autoReconnect: options.autoReconnect ?? true,
      reconnectDelayMs: options.reconnectDelayMs ?? 1000,
      debug: options.debug ?? false,
    };
  }

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.updateStatus("connecting");
    this.ws = new WebSocket(this.opts.wsUrl);

    this.ws.onopen = () => {
      this.log("connected");
      this.updateStatus("open");
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data) as TaupyMessage;
        this.dispatch(msg);
      } catch (err) {
        this.log("Failed to parse message", err);
      }
    };

    this.ws.onclose = () => {
      this.log("closed");
      this.updateStatus("closed");
      if (this.opts.autoReconnect) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (err) => {
      this.log("error", err);
    };
  }

  close() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(payload: TaupyMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload));
    } else {
      this.log("send skipped, socket not open");
    }
  }

  on(type: string, handler: Listener) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)!.add(handler);
    return () => this.off(type, handler);
  }

  off(type: string, handler: Listener) {
    this.listeners.get(type)?.delete(handler);
  }

  onStatus(handler: StatusListener) {
    this.statusListeners.add(handler);
    return () => this.statusListeners.delete(handler);
  }

  private dispatch(msg: TaupyMessage) {
    this.listeners.get(msg.type)?.forEach((cb) => cb(msg));
  }

  private updateStatus(status: "connecting" | "open" | "closed") {
    this.statusListeners.forEach((cb) => cb(status));
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, this.opts.reconnectDelayMs);
  }

  private log(...args: any[]) {
    if (this.opts.debug) {
      // eslint-disable-next-line no-console
      console.log("[TaupyClient]", ...args);
    }
  }
}
