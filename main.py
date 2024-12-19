import os
import random
import string
import json
import sys
import signal
import subprocess
from multiprocessing import Process, cpu_count, Lock, Value, current_process
import psutil

DEFAULT_INT_MIN = -2**31
DEFAULT_INT_MAX = 2**31 - 1
DEFAULT_STRING_MIN_LENGTH = 1
DEFAULT_STRING_MAX_LENGTH = 100

# Shared Variable and lock
command_counter = Value('i', 1)  # shared variable for cmd order
counter_lock = Lock()

def terminate_processes_and_exit(flag: int = 0):
    """
    Terminates all processes initiated by the current Python script
    and exits the script and restart fuzzing
    """

    if flag == 1:
        print("no devices/emulators found")

    parent_process = psutil.Process()

    children_ = parent_process.children(recursive=True)
    for child in children_:
        child.terminate()

    if flag == 0: 
        print("Exiting script.")
        print("Restarting fuzzing")
        os.system("python main.py")
    exit(1)

def parse_json(json_file):
    """
    Parse JSON file to extract transactions.
    """
    with open(json_file, 'r') as file:
        data = json.load(file)
    transactions = data.get('transactions', [])
    return transactions

def generate_random_integer(min_val=None, max_val=None):
    """
    Generate a random integer within a given range.
    If no range is provided, use full int range.
    """
    if min_val is None:
        min_val = DEFAULT_INT_MIN
    if max_val is None:
        max_val = DEFAULT_INT_MAX
    return random.randint(min_val, max_val)

def generate_random_float(min_val=None, max_val=None):
    """
    Generate a random float within a given range.
    If no range is provided, use default float range.
    """
    if min_val is None:
        min_val = -1.0e+38
    if max_val is None:
        max_val = 1.0e+38
    return round(random.uniform(min_val, max_val), 6)

def generate_random_double(min_val=None, max_val=None):
    """
    Generate a random double within a given range.
    If no range is provided, use default float range.
    """
    if min_val is None:
        min_val = -1.0e+308
    if max_val is None:
        max_val = 1.0e+308
    return round(random.uniform(min_val, max_val), 12)



def generate_random_string(min_length=None, max_length=None):
    """
    Generate a random string with a length within a given range.
    Includes letters, digits, and special characters.
    """
    if min_length is None:
        min_length = DEFAULT_STRING_MIN_LENGTH
    if max_length is None:
        max_length = DEFAULT_STRING_MAX_LENGTH
    length = random.randint(min_length, max_length)
    all_characters = ''.join(chr(i) for i in range(32, 127))  # Printable ASCII
    all_characters += ''.join(chr(i) for i in range(128, 50000))  # Unicode BMP
    return ''.join(random.choices(all_characters, k=length))

def generate_boolean():
    """
    Generate a random boolean value.
    """
    return "true" if random.choice([True, False]) else "false"

def execute_transaction(service_name, code, data, log_file):
    """
    Execute a system transaction using adb shell service call and log the results.
    """
    cmd = ['adb', 'shell', 'service', 'call', service_name, str(code)]
    if data:
        cmd.extend(data)
    
        
    with counter_lock:
        current_cmd_id = command_counter.value
        command_counter.value += 1

    try:
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        # Safely handle NoneType for stdout and stderr
        stdout = result.stdout if result.stdout is not None else ""
        stderr = result.stderr if result.stderr is not None else ""

        if "no devices/emulators found" in stdout or "no devices/emulators found" in stderr:
            terminate_processes_and_exit(1)

        if "does not exist" in stdout or "does not exist" in stderr:
            log_file.write(f"crash!! [{current_cmd_id}] Command: {' '.join(cmd)}\n".encode("utf-8", "replace").decode("utf-8"))
            log_file.write(f"Output: {result.stdout}, {result.stderr}\n".encode("utf-8", "replace").decode("utf-8"))
            terminate_processes_and_exit()
        # Log the command and output
        log_file.write(f"[{current_cmd_id}] Command: {' '.join(cmd)}\n".encode("utf-8", "replace").decode("utf-8"))
        log_file.write(f"Output: {result.stdout}\n".encode("utf-8", "replace").decode("utf-8"))
    except subprocess.TimeoutExpired:
        # Log timeout information
        log_file.write(f"[{current_cmd_id}] Timeout for command: {' '.join(cmd)}\n")

def fuzz_transactions(transactions, log_file):
    """
    Fuzz transactions by iterating over each transaction and generating random inputs.
    """
    for transaction in transactions:
        service_name = transaction.get('service_name')
        code = transaction.get('code')
        input_types = transaction.get('input_types', [])

        if not service_name or code is None:
            log_file.write("Invalid transaction data, skipping...\n")
            continue

        fuzz_data = []
        for input_type in input_types:
            input_type_name = input_type.get('type')
            
            if input_type_name == 'i32':
                # Generate random 32-bit integer
                min_val, max_val = input_type.get('range', [None, None])
                fuzz_data.append(f"i32 {generate_random_integer(min_val, max_val)}")
            elif input_type_name == 'i64':
                # Generate random 64-bit integer
                min_val, max_val = input_type.get('range', [None, None])
                fuzz_data.append(f"i64 {generate_random_integer(min_val, max_val)}")
            elif input_type_name == 'iarr':
                min_val, max_val = input_type.get('range', [None, None])
                elements = generate_random_integer(0, 1019)
                for _ in range(elements): 
                    fuzz_data.append(f"i32 {generate_random_integer(min_val, max_val)}")  # 각 원소 추가
            elif input_type_name == 'sarr':
                min_val, max_val = input_type.get('range', [None, None])
                elements = generate_random_integer(0, 50)
                for _ in range(elements): 
                    fuzz_data.append(f"s16 {generate_random_string(min_val, max_val)}")  # 각 원소 추가
            elif input_type_name == 'f':
                # Generate random single-precision float
                min_val, max_val = input_type.get('range', [None, None])
                fuzz_data.append(f"f {generate_random_float(min_val, max_val)}")
            elif input_type_name == 'd':
                # Generate random double-precision float
                min_val, max_val = input_type.get('range', [None, None])
                fuzz_data.append(f"d {generate_random_double(min_val, max_val)}")
            elif input_type_name == 's16':
                # Generate random UTF-16 string
                min_length, max_length = input_type.get('length', [None, None])
                fuzz_data.append(f"s16 \"{generate_random_string(min_length, max_length)}\"")
            elif input_type_name == 'null':
                # Append null value
                fuzz_data.append("null")
            elif input_type_name == 'fd':
                # Append file descriptor (example: '/dev/null')
                file_path = input_type.get('file')
                fuzz_data.append(f"fd {file_path}")
            elif input_type_name == 'afd':
                # Append ashmem file descriptor (example: '/dev/ashmem')
                file_path = input_type.get('file')
                fuzz_data.append(f"afd {file_path}")
            elif input_type_name == 'nfd':
                # Append file descriptor (example: 3)
                file_path = input_type.get('num')
                fuzz_data.append(f"afd {file_path}")
            else:
                log_file.write(f"Unsupported input type: {input_type_name}, skipping...\n")
                continue


        execute_transaction(service_name, code, fuzz_data, log_file)

def worker_process(transactions, log_file_path):
    """
    Worker process to run fuzz_transactions in a loop.
    """
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        while True:
            fuzz_transactions(transactions, log_file)

def start_logcat(log_file="log.txt"):
    """
    Start adb logcat and save the output to a file.
    """
    with open(log_file, "w") as file:
        process = subprocess.Popen(['adb', 'logcat'], stdout=file, stderr=subprocess.STDOUT)
    return process

def start_crashcat(crash_file="crash.txt"):
    """
    Start adb logcat -b crash and save the output to a file.
    """
    with open(crash_file, "w") as file:
        process = subprocess.Popen(['adb', 'logcat', '-b', 'crash'], stdout=file, stderr=subprocess.STDOUT)
    return process


if __name__ == "__main__":
    json_file_path = './services.json'  # System service transactions JSON file
    
    if not os.path.exists(json_file_path):
        print(f"JSON file not found: {json_file_path}")
        exit(1)

    transactions = parse_json(json_file_path)  # Parse JSON file
    
    # Start logcat process
    logcat_process = start_logcat()
    crash_process = start_crashcat()

    log_file_path = "result.txt"  # Log file path

    # Determine the number of processes to spawn
    num_processes = cpu_count()  # Use the number of CPU cores
    print(num_processes)
    processes = []

    try:
        for _ in range(num_processes):
            # Create and start a new process
            process = Process(target=worker_process, args=(transactions, log_file_path))
            process.start()
            processes.append(process)

        # Wait for all processes to complete
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        # Terminate all processes on interrupt
        for process in processes:
            process.terminate()
                # Terminate logcat process
        logcat_process.terminate()
        crash_process.terminate()
        os.system("python main.py")
        print("All processes and logcat terminated.")
