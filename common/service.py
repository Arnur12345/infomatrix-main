import logging
import multiprocessing


class ServiceBase(multiprocessing.Process):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.running = multiprocessing.Event()  # Use an Event to control the state
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def run(self):
        """Override this method in subclasses to define the service's behavior."""
        raise NotImplementedError

    def start(self):
        """Start the service in a separate process."""
        if not self.running.is_set():
            self.running.set()  # Set the running flag to True
            super().start()  # Use the 'start' method of multiprocessing.Process

    def stop(self):
        """Stop the service."""
        if self.running.is_set():
            self.running.clear()  # Clear the running flag
            self.join()  # Wait for the process to finish
            self.logger.info("Service stopped.")
