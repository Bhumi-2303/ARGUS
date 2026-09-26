import { useEffect, useRef, useState, useCallback } from 'react';

export interface StreamTelemetryEvent {
  event_id: string;
  timestamp: string;
  domain: string;
  features: {
    pkt_mean_to_max: number;
    tcp_flag_density: number;
    log_pkt_mean: number;
    log_pkt_max: number;
  };
  anomaly_score: number;
  prediction: number;
  model_used: string;
}

export type StreamStatus = 'connected' | 'connecting' | 'paused' | 'reconnecting' | 'disconnected' | 'error';

export interface UseLiveStreamOptions {
  domain?: string;
  initialSpeed?: number;
  maxBuffer?: number;
  autoConnect?: boolean;
}

export function useLiveStream(options: UseLiveStreamOptions = {}) {
  const {
    domain = 'ciciot',
    initialSpeed = 1,
    maxBuffer = 100,
    autoConnect = true,
  } = options;

  const [status, setStatus] = useState<StreamStatus>('disconnected');
  const [speed, setSpeedState] = useState<number>(initialSpeed);
  const [isPaused, setIsPaused] = useState<boolean>(!autoConnect);
  const [events, setEvents] = useState<StreamTelemetryEvent[]>([]);
  const [anomalyCount, setAnomalyCount] = useState<number>(0);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setStatus('connecting');
    const apiBase = import.meta.env.VITE_API_BASE_URL || '';
    const url = `${apiBase}/api/v1/stream/events?domain=${domain}&speed=${speed}`;

    try {
      const es = new EventSource(url);
      eventSourceRef.current = es;

      es.onopen = () => {
        setStatus('connected');
      };

      es.onmessage = (evt) => {
        if (isPaused) return;

        try {
          const data: StreamTelemetryEvent = JSON.parse(evt.data);
          setEvents((prev) => {
            const next = [data, ...prev];
            return next.slice(0, maxBuffer);
          });
          if (data.prediction === 1) {
            setAnomalyCount((c) => c + 1);
          }
        } catch {
          // Ignore malformed message
        }
      };

      es.onerror = () => {
        setStatus('reconnecting');
        es.close();

        // Attempt reconnect after 3s
        if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = window.setTimeout(() => {
          if (!isPaused) {
            connect();
          }
        }, 3000);
      };
    } catch {
      setStatus('error');
    }
  }, [domain, speed, isPaused, maxBuffer]);

  const pause = useCallback(() => {
    setIsPaused(true);
    setStatus('paused');
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  const resume = useCallback(() => {
    setIsPaused(false);
    connect();
  }, [connect]);

  const setSpeed = useCallback((newSpeed: number) => {
    setSpeedState(newSpeed);
  }, []);

  const reconnect = useCallback(() => {
    setIsPaused(false);
    connect();
  }, [connect]);

  const clear = useCallback(() => {
    setEvents([]);
    setAnomalyCount(0);
  }, []);

  useEffect(() => {
    if (autoConnect && !isPaused) {
      connect();
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect, autoConnect, isPaused]);

  return {
    status,
    speed,
    isPaused,
    events,
    latestEvent: events[0] || null,
    anomalyCount,
    pause,
    resume,
    setSpeed,
    reconnect,
    clear,
  };
}
