# ⌚ WatchOut

We are **WatchOut**, a smartwatch vulnerability analysis team from **BOB (Best of the Best)** in South Korea.

We have developed both a **fuzzer for marformed input** and a **fuzzer for formatted input**, and this fuzzer is the **formatted fuzzer**.

### 📜 **Overview**

The **AngelFuzzer** is a Python-based tool designed to **fuzz android smartwatch system services** via the `adb shell service call` command. It targets services to identify potential vulnerabilities, crashes, and abnormal behaviors.

The fuzzer randomly generates inputs of various types (integers, strings, arrays, booleans, etc.) to test system service stability, collect outputs, and log any crashes.


### 🚀 **Features**

1. **System Service Fuzzing**:
    - Fuzzes transactions by calling system services with randomly generated inputs.
    - Supports various input types: integers, strings, arrays, booleans, and file descriptors.
2. **Crash Monitoring**:
    - Continuously logs crashes using `adb logcat -b crash`.
3. **Parallel Execution**:
    - Leverages multiple CPU cores to run fuzzing in parallel for better performance.
4. **Automatic Restart**:
    - Restarts the fuzzing process after detecting specific issues (e.g., no devices found).
5. **Customizable Input Generation**:
    - Supports range-based inputs for integers, floats, and strings.
    - Can fuzz array structures (e.g., iarr, sarr).

### 🛠️ **Prerequisites**

1. **Python Environment**:
    - Python 3.8
    - Required libraries: `psutil`
    
    Install dependencies:
    
    ```bash
    pip install psutil
    ```
    
2. **ADB** (Android Debug Bridge):
    - Ensure `adb` is installed and added to your PATH.
    - The smartwatch must be connected via ADB (USB or Wireless).
3. **Target Device**:
    - An android based smartwatch with developer options enabled.
    - Properly configured ADB connection to the target device.
4. **JSON Configuration File**:
    - A `services.json` file containing details of the services and transactions to fuzz.
    - Example structure:
        
        ```json
        {
          "transactions": [
            {
              "service_name": "watchout",
              "code": 5,
              "input_types": [{"type": "s16", "length": [1, 20]}]
            }
          ]
        }
        ```
        

### ⚙️ **How to Use**

1. **Clone the Repository**
2. **Connect the Smartwatch**:
    - Ensure the smartwatch is connected via ADB.
    - Verify the connection:
        
        ```bash
        adb devices
        ```
        
3. **Prepare the JSON Configuration**:
    - Create a `services.json` file defining the target services and their inputs.
4. **Run the Fuzzer**:
    - Execute the main script:
        
        ```bash
        python main.py
        ```
        
5. **Monitor the Logs**:
    - Outputs and crashes will be logged in the following files:
        - `result.txt`: Fuzzing results
        - `log.txt`: System logs from `adb logcat`
        - `crash.txt`: Crash logs from `adb logcat -b crash`
6. **Analyze Results**:
    - Review `result.txt` and `crash.txt` for crashes, unexpected outputs, or vulnerabilities.

### 📝 **Example JSON Configuration**

```json
 {
    "transactions":[
    {
        "service_name": "iccc",
        "code": 1,
        "input_types": [
            {"type": "i32", "range": [0,100]},
        ]
    },
    {
        "service_name": "iccc",
        "code": 2,
        "input_types": [
            {"type": "i32"},
            {"type": "i32"}
        ]
    }
}
```

- input_type
    - i32: int (32bit)
        - range: minimum integer and maximum integer
    - i64: int (64bit)
        - range: minimum integer and maximum integer
    - iarr: int array
        - range: minimum integer and maximum integer
        - array size is random
    - sarr: string array
        - range: minimum length and maximum length
        - array size is random
    - f: float
        - range: minimum float and maximum float
    - d: double
        - range: minimum double and maximum double
    - s16: string
        - length: minimum length and maximum length
    - null: null
    - fd: file descriptor
    - afd: ashmem file descriptor
    - nfd: file descriptor
        - num: number

### 🔄 **Restart Mechanism**

- If the device disconnects (`no devices/emulators found`), the fuzzer will exit and not restart.
- Crashes that result in abnormal outputs (e.g., service does not exist) will trigger a restart.

### 💻 **Output Files**

- **`result.txt`**: Logs each command executed and its output.
- **`log.txt`**: Complete ADB logcat output.
- **`crash.txt`**: ADB logcat crash output only.

### 🛡️ **Disclaimer**

This tool is intended for **educational and research purposes only**. Use it on devices and services you own or have permission to test. The author is not responsible for any misuse or damage caused.

### 🌟 **Acknowledgments**

Special thanks to the open-source community and tools that made this project possible.
