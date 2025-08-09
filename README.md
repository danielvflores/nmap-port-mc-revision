# Parallel Nmap Port Scanner

A high-performance, multi-threaded port scanner built with Python that leverages nmap for comprehensive network reconnaissance. Designed for cybersecurity professionals and penetration testers.

## Features

- **Parallel Scanning**: Multi-threaded execution for faster scan completion
- **Domain Resolution**: Automatic DNS resolution for domain names
- **Multiple Scan Types**: Fast, full, and custom port range options
- **Real-time Progress**: Live timer and completion tracking
- **Comprehensive Logging**: Detailed scan results saved to timestamped files
- **Privilege Detection**: Automatic administrator privilege checking
- **Input Validation**: Robust IP address and domain name validation
- **Error Handling**: Timeout protection and error recovery

## Requirements

- Python 3.6+
- nmap installed and accessible from command line
- Administrator privileges (recommended for SYN scans)

### Installing nmap

**Windows:**
```bash
# Download from https://nmap.org/download.html
# Or using chocolatey
choco install nmap
```

**Linux:**
```bash
sudo apt-get install nmap    # Ubuntu/Debian
sudo yum install nmap        # CentOS/RHEL
```

## Usage

1. Clone or download the script
2. Run with Python:
```bash
python script.py
```

3. Follow the interactive prompts:
   - Enter target IP address or domain name
   - Select scan type (Fast/Full/Custom)
   - Wait for results

## Scan Types

### 1. Fast Scan
- **Port Range**: 1-1000
- **Use Case**: Quick reconnaissance of common services
- **Duration**: ~30 seconds to 2 minutes

### 2. Full Scan
- **Port Range**: 1-30,000 (divided into 6 parallel chunks)
- **Use Case**: Comprehensive port discovery
- **Duration**: 5-30 minutes depending on target

### 3. Custom Scan
- **Port Range**: User-defined
- **Use Case**: Targeted scanning of specific port ranges
- **Duration**: Varies based on range size

## Technical Details

### Scanning Parameters
- **SYN Scan** (`-sS`): Default for privileged users (faster, stealthier)
- **TCP Connect** (`-sT`): Fallback for non-privileged users
- **Service Detection** (`-sV`): Identifies service versions
- **No Ping** (`-Pn`): Bypasses host discovery
- **Timing** (`-T4`): Aggressive timing for faster scans
- **Retries** (`--max-retries 2`): Limited retries for efficiency

### Parallel Execution
- **Thread Pool**: Up to 6 concurrent nmap processes
- **Chunk Size**: 5,000 ports per thread maximum
- **Timeout**: 5-minute timeout per port range
- **Dynamic Workers**: Adjusts worker count based on port ranges

## Output

### Console Output
```
=== Parallel Nmap Port Scanner ===
Enter IP address or domain to scan: example.com
Domain example.com resolved to IP: 93.184.216.34
Select scan type:
1. Fast (common ports: 1-1000)
2. Full (ports 1-30000)
3. Custom
Option (1-3): 1
Saving logs to: src/logs/nmap_scan_93_184_216_34_20250809_143022.txt
Starting scan with 1 parallel threads...
Elapsed time: 00:15 | Completed: 0/1

Scanning ports 1-1000...
--- Result for ports 1-1000 ---
Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for example.com (93.184.216.34)
Host is up (0.12s latency).
PORT    STATE SERVICE VERSION
80/tcp  open  http    nginx
443/tcp open  https   nginx

Scan completed in: 00:45
Logs saved to: src/logs/nmap_scan_93_184_216_34_20250809_143022.txt
```

### Log Files
- **Location**: `src/logs/`
- **Format**: `nmap_scan_[IP]_[TIMESTAMP].txt`
- **Content**: Complete nmap output with metadata

## Security Considerations

### Ethical Usage
- Only scan networks you own or have explicit permission to test
- Respect rate limits and terms of service
- Use responsibly for legitimate security testing

### Legal Compliance
- Ensure compliance with local laws and regulations
- Obtain proper authorization before scanning external networks
- Consider using in isolated lab environments

## Common Use Cases

### Penetration Testing
- Network reconnaissance phase
- Service enumeration
- Attack surface identification

### Minecraft Server Discovery
- Finding non-standard ports (beyond 25565)
- Identifying server software versions
- Discovering auxiliary services (web panels, databases)

### Network Security Auditing
- Port exposure assessment
- Service inventory
- Vulnerability identification preparation

## Troubleshooting

### Permission Issues
```bash
# Run as administrator (Windows)
# Run with sudo (Linux)
sudo python script.py
```

### Nmap Not Found
```bash
# Verify nmap installation
nmap --version

# Add nmap to PATH if necessary
```

### Slow Performance
- Check network connectivity
- Reduce port ranges for faster results
- Ensure target host is responsive

### Timeout Errors
- Increase timeout value in `run_nmap()` function
- Check firewall settings on target
- Verify network stability

## Advanced Configuration

### Modifying Scan Parameters
Edit the `run_nmap()` function to customize:
- Scan techniques (`-sS`, `-sT`, `-sU`)
- Timing templates (`-T1` to `-T5`)
- Additional options (`--script`, `-A`, `-O`)

### Custom Port Ranges
For Minecraft-specific scanning:
```python
minecraft_ports = [25565, 25566, 25567, 19132, 19133, 8123]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This tool is provided for educational and authorized security testing purposes only. Users are responsible for compliance with applicable laws and regulations.

## Disclaimer

This software is intended for legitimate security testing and educational purposes. The authors are not responsible for any misuse or damage caused by this tool. Always ensure you have proper authorization before scanning any network
