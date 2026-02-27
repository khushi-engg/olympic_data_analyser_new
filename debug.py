# debug.py
import os
import sys
import pandas as pd

print("=" * 50)
print("DIAGNOSTIC INFORMATION")
print("=" * 50)

# Current working directory
print(f"\n1. Current working directory: {os.getcwd()}")
print(f"2. Python path: {sys.executable}")
print(f"3. Script location: {__file__}")

# List all files in current directory
print(f"\n4. Files in current directory:")
for file in os.listdir():
    size = os.path.getsize(file) if os.path.isfile(file) else 0
    print(f"   - {file} ({size} bytes)")

# Check parent directory
print(f"\n5. Files in parent directory:")
parent_dir = os.path.dirname(os.getcwd())
if os.path.exists(parent_dir):
    for file in os.listdir(parent_dir):
        print(f"   - {file}")

# Try to load athlete_events.csv with different methods
print(f"\n6. Attempting to load athlete_events.csv:")

# Method 1: Direct path
try:
    df1 = pd.read_csv('athlete_events.csv', encoding='latin1', nrows=5)
    print(f"   ✅ Method 1 SUCCESS: Loaded {len(df1)} rows")
    print(f"   Columns: {df1.columns.tolist()}")
except Exception as e:
    print(f"   ❌ Method 1 FAILED: {str(e)}")

# Method 2: With different encoding
try:
    df2 = pd.read_csv('athlete_events.csv', encoding='utf-8', nrows=5)
    print(f"   ✅ Method 2 (utf-8) SUCCESS")
except Exception as e:
    print(f"   ❌ Method 2 FAILED: {str(e)}")

# Method 3: With engine='python'
try:
    df3 = pd.read_csv('athlete_events.csv', encoding='latin1', engine='python', nrows=5)
    print(f"   ✅ Method 3 (python engine) SUCCESS")
except Exception as e:
    print(f"   ❌ Method 3 FAILED: {str(e)}")

# Method 4: Check if file exists first
if os.path.exists('athlete_events.csv'):
    file_size = os.path.getsize('athlete_events.csv')
    print(f"   📁 File exists! Size: {file_size} bytes")
else:
    print(f"   ❌ File does NOT exist!")

print("\n" + "=" * 50)
print("PREPROCESSOR TEST")
print("=" * 50)

# Test preprocessor
try:
    import preprocessor

    print("✅ preprocessor module imported")

    df = preprocessor.preprocess()
    print(f"✅ preprocess() returned DataFrame with shape: {df.shape}")
    print(f"✅ Columns: {df.columns.tolist()}")

    if df.empty:
        print("❌ DataFrame is EMPTY!")
    else:
        print(f"✅ First few rows:")
        print(df.head())

except Exception as e:
    print(f"❌ Error in preprocessor: {str(e)}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 50)