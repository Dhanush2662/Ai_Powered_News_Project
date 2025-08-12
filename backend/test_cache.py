#!/usr/bin/env python3
"""
Test script to verify Redis caching functionality
"""

import asyncio
import time
from dotenv import load_dotenv
from utils.cache import cache, redis_client, clear_cache
from config import Config

# Load environment variables
load_dotenv()

# Test function with caching
@cache(prefix="test")
async def test_function(param1, param2):
    """Test function that simulates a slow API call"""
    print(f"Executing test_function with params: {param1}, {param2}")
    # Simulate slow API call
    await asyncio.sleep(1)
    return {"result": f"Result for {param1} and {param2}", "timestamp": time.time()}


async def run_tests():
    """Run tests to verify caching functionality"""
    print("\n===== Testing Redis Caching =====\n")
    
    # Clear any existing cache
    clear_cache("test")
    print(f"Cache TTL set to {Config.CACHE_TTL_SECONDS} seconds")
    
    # First call - should execute the function
    print("\nFirst call (should execute the function):")
    start = time.time()
    result1 = await test_function("value1", "value2")
    duration1 = time.time() - start
    print(f"Result: {result1}")
    print(f"Duration: {duration1:.4f} seconds")
    
    # Second call with same parameters - should use cache
    print("\nSecond call with same parameters (should use cache):")
    start = time.time()
    result2 = await test_function("value1", "value2")
    duration2 = time.time() - start
    print(f"Result: {result2}")
    print(f"Duration: {duration2:.4f} seconds")
    print(f"Cache speedup: {duration1/duration2:.2f}x faster")
    
    # Third call with different parameters - should execute the function
    print("\nThird call with different parameters (should execute the function):")
    start = time.time()
    result3 = await test_function("value3", "value4")
    duration3 = time.time() - start
    print(f"Result: {result3}")
    print(f"Duration: {duration3:.4f} seconds")
    
    # Verify cache keys
    print("\nCache keys:")
    keys = redis_client.keys("test:*")
    for key in keys:
        print(f"- {key}")
        value = redis_client.get(key)
        print(f"  Value: {value[:50]}..." if len(value) > 50 else f"  Value: {value}")
    
    # Clear specific cache
    print("\nClearing specific cache prefix:")
    deleted = clear_cache("test")
    print(f"Deleted {deleted} keys")
    
    # Verify cache is cleared
    keys = redis_client.keys("test:*")
    print(f"Remaining keys with prefix 'test:': {len(keys)}")


if __name__ == "__main__":
    asyncio.run(run_tests())
    print("\nCache test completed!")