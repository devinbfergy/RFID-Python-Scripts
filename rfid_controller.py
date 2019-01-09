import mercury
import logging
from sys import stdout
from time import sleep
from multiprocessing import Process, Queue, get_logger

logger = get_logger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def read_tags_worker(queue_of_tags: Queue):
    """
    
    """
    reader = mercury.Reader("tmr:///dev/ttyS4", baudrate=115200)
    reader.set_region("NA2")
    reader.set_read_plan([1], "GEN2", read_power=500)
    try:
        logger.info("Read Worker is Attempting to read")
        while True:
            try:
                tags = reader.read(timeout=250)
            except RuntimeError:
                pass
            if len(tags) != 0:
                for tag in tags:
                    queue_of_tags.put(tag.epc)
            sleep(.25)

    except KeyboardInterrupt:
        logger.info("keyboard interrupt in Read Worker")
    finally:
        logger.info("Read Worker done reading")
        reader.stop_reading()
        queue_of_tags.close()


def main():
    tags_queue = Queue()
    unique_tags = set()

    reader_worker = Process(target=read_tags_worker, args=(tags_queue,))

    logger.info("Starting Read Worker")
    reader_worker.start()
    try:
        while True:
            item = tags_queue.get()
            if item is None:
                break
            
            unique_tags.add(item)
    except KeyboardInterrupt:
        logger.info("Keyboard Interupt in Main Thread")
        logger.info("Joining Read Worker")
        reader_worker.join()
        logger.info("Emptying Queue")
        while tags_queue.full():
            item = tags_queue.get()
            if item is None:
                break
            
            unique_tags.add(item)
    finally:
        print(unique_tags)
        print(len(unique_tags))
        logger.info("Main Thread exiting")
        for handler in logger.handlers:
            handler.close()
            logger.removeFilter(handler)
        
if __name__ == "__main__":
    main()
