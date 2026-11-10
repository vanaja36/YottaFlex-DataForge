from src.logger import get_logger

logger = get_logger()

logger.info("FlowForge logging test successful")
logger.warning("This is a sample warning")
logger.error("This is a sample error")

print("Logging test completed!")
