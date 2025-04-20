
# 🌟 LuniTack: The Ultimate Simulation Tool

## 🚀 Powered by Spacie

LuniTack is a high-performance network simulation tool designed for educational and testing purposes. It allows users to simulate high network traffic scenarios with precise control over parameters like packet size, rate limit, and thread count. **Use responsibly and only in authorized environments.**

---

## Features
- **🌐 High Traffic Simulation**: Simulates a massive number of network packets to a target IP and port.
- **⚙️ Customizable Parameters**:
  - Target IP and Port
  - Duration of Simulation
  - Number of Threads
  - Rate Limit (Packets per Second)
  - Payload Size
- **🔒 Simulation Mode**: Enables a safe simulation without sending actual packets.
- **📊 Progress Tracking**: Real-time progress updates using a dynamic progress bar.
- **🛡️ System Resource Checks**: Alerts if system CPU or memory usage is high.
- **📝 Detailed Logging**: Logs all activities and errors to `ddos_simulation.log`.
- **📄 Report Generation**: Outputs a detailed report of the simulation to `ddos_report.txt`.

---

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ice-exe/LuniTack.git
   cd LuniTack
   ```

2. **Install Required Libraries**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage
### Command-Line Arguments
Run LuniTack directly from the terminal with the following options:
```bash
python LuniTack.py --ip <target_ip> --port <target_port> --duration <seconds> \
                  --threads <thread_count> --rate <packets_per_second> --payload <bytes>
```

Example:
```bash
python LuniTack.py --ip 192.168.1.10 --port 80 --duration 60 --threads 10 --rate 200 --payload 1024
```

### Interactive Mode
If you do not provide arguments, LuniTack will guide you through an interactive setup.

---

## Simulation Mode
Enable simulation mode to test without sending packets:
```bash
python LuniTack.py --simulate
```

---

## Output
- **🛠 Logs**: All activity is logged in `ddos_simulation.log`.
- **📊 Report**: A detailed report is saved as `ddos_report.txt` after execution.

---

## System Requirements
- Python 3.7 or later
- Libraries:
  - `socket`
  - `threading`
  - `random`
  - `time`
  - `sys`
  - `logging`
  - `psutil`
  - `datetime`
  - `tqdm`
  - `argparse`

---

## ⚠️ Disclaimer
LuniTack is intended for **educational and authorized testing purposes only**. Unauthorized use of this tool is illegal and unethical. The creators are not responsible for any misuse. Use with caution and responsibility!

---

## License
This project is licensed under the MIT License.
