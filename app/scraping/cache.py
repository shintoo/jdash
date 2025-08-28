import functools
import pickle
import os
import time
from datetime import datetime, timedelta
import hashlib

def cache(cache_dir=".cache", expiry=timedelta(hours=2)):
    """
    Decorator to cache function results to a pickle file, expiring after 1 day.

    Args:
        cache_dir (str): Directory to store cache files. Defaults to ".cache"
    """
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique cache key based on function name and arguments
            func_name = func.__name__
            module_name = func.__module__

            # Create a hash of the arguments to make a unique key
            arg_key = _create_arg_hash(args, kwargs)
            cache_key = f"{module_name}.{func_name}.{arg_key}"

            # Create cache file path
            cache_file = os.path.join(cache_dir, f"{cache_key}.pkl")

            # Check if cache exists and is still valid
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'rb') as f:
                        cached_data = pickle.load(f)

                    # Check if cache is still valid (within 1 day)
                    if datetime.now() - cached_data['timestamp'] < expiry:
                        print(f"Cache hit for {func_name}")
                        return cached_data['result']
                    else:
                        print(f"Cache expired for {func_name}")

                except (pickle.UnpicklingError, EOFError, KeyError, OSError) as e:
                    print(f"Cache read error for {func_name}: {e}")
                    # Cache is corrupted or invalid, remove it
                    try:
                        os.remove(cache_file)
                    except OSError:
                        pass

            # Cache miss or expired - execute function
            print(f"Cache miss for {func_name}, executing function...")
            result = func(*args, **kwargs)

            # Save result to cache
            try:
                cache_data = {
                    'result': result,
                    'timestamp': datetime.now(),
                    'function': f"{module_name}.{func_name}"
                }

                with open(cache_file, 'wb') as f:
                    pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)

            except (OSError, pickle.PicklingError) as e:
                print(f"Failed to save cache for {func_name}: {e}")

            return result

        return wrapper
    return decorator

def _create_arg_hash(args, kwargs):
    """Create a hash from function arguments to use as part of the cache key."""
    # Convert args and kwargs to a string representation
    # This handles most common types, but may need extension for complex objects
    arg_str = str(args) + str(sorted(kwargs.items()))

    # Create MD5 hash of the argument string
    return hashlib.md5(arg_str.encode('utf-8')).hexdigest()[:16]

# Example usage and testing
if __name__ == "__main__":
    import time

    @cache()
    def expensive_function(x, y):
        """Simulate an expensive computation."""
        print(f"Computing expensive_function({x}, {y})...")
        time.sleep(1)  # Simulate work
        return x * y + 42

    @cache()
    def get_user_data(user_id):
        """Simulate fetching user data from database."""
        print(f"Fetching data for user {user_id}...")
        time.sleep(0.5)
        return {
            'id': user_id,
            'name': f'User_{user_id}',
            'timestamp': time.time()
        }

    # Test the caching
    print("=== First call ===")
    result1 = expensive_function(5, 10)
    print(f"Result: {result1}")

    print("\n=== Second call (should be cached) ===")
    result2 = expensive_function(5, 10)  # Should use cache
    print(f"Result: {result2}")

    print("\n=== Different arguments (cache miss) ===")
    result3 = expensive_function(3, 7)  # Different args, cache miss
    print(f"Result: {result3}")

    print("\n=== Using keyword arguments ===")
    result4 = expensive_function(x=5, y=10)  # Should be cached (same as first call)
    print(f"Result: {result4}")

    print("\n=== Testing another function ===")
    user_data = get_user_data(123)
    print(f"User data: {user_data}")

    user_data2 = get_user_data(1234)  # Should be cached
    print(f"User data: {user_data2}")