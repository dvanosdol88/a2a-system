#!/usr/bin/env python3
import time, subprocess, signal, os
import logging
import argparse
import threading

shutdown_event = threading.Event()
logging.basicConfig(filename='logs/orchestrator.log', level=logging.INFO, format='%(asctime)s - %(message)s')

PROCESSES = {
    'jules': ['python', 'api/jules_server.py'],
    'connector': ['bash', 'agents/run_ai_connector.sh']
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis-url", help="Redis URL")
    parser.add_argument("--openai-key", help="OpenAI API key")
    args = parser.parse_args()

    env = os.environ.copy()
    if args.redis_url:
        env["REDIS_URL"] = args.redis_url
    if args.openai_key:
        env["OPENAI_API_KEY"] = args.openai_key

    processes = {}
    for name, cmd_args in PROCESSES.items():
        p = subprocess.Popen(cmd_args, env=env)
        processes[name] = p
        logging.info(f"Started {name} with PID {p.pid}")

    try:
        while not shutdown_event.is_set():
            for name, p in processes.items():
                if p.poll() is not None:
                    logging.info(f"{name} has exited with code {p.returncode}. Restarting...")
                    p = subprocess.Popen(PROCESSES[name], env=env)
                    processes[name] = p
                    logging.info(f"Restarted {name} with PID {p.pid}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Shutting down all processes...")
        for p in processes.values():
            p.send_signal(signal.SIGINT)
        for p in processes.values():
            p.wait()
        logging.info("All processes have been shut down.")

if __name__ == "__main__":
    main()
