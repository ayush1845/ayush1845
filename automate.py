# Check if necessary tools are installed
command -v nmap >/dev/null 2>&1 || { echo >&2 "Nmap is required but not installed. Exiting..."; exit 1; }
command -v lynis >/dev/null 2>&1 || { echo >&2 "Lynis is required but not installed. Exiting..."; exit 1; }
command -v sendmail >/dev/null 2>&1 || { echo >&2 "sendmail is required but not installed. Exiting..."; exit 1; }

# Define server details
SERVER_IP="192.168.1.10"  # Replace with your server's IP address or hostname
ADMIN_EMAIL="admin@example.com"  # Replace with the admin's email address
HOSTNAME=$(hostname)

# Directories for storing logs and reports
LOG_DIR="/var/log/security_scan"
REPORT_DIR="/tmp/security_reports"

mkdir -p $LOG_DIR
mkdir -p $REPORT_DIR

# Timestamp for reports
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Function to send an email notification
send_email() {
    SUBJECT=$1
    BODY=$2
    echo -e "$BODY" | sendmail -v $ADMIN_EMAIL -s "$SUBJECT"
}

# 1. Run Nmap Scan for open ports
nmap -sS -T4 -p- $SERVER_IP > $REPORT_DIR/nmap_scan_$TIMESTAMP.txt
echo "Nmap scan completed for $SERVER_IP" >> $LOG_DIR/security_log_$TIMESTAMP.log

# 2. Run Lynis security audit
lynis audit system > $REPORT_DIR/lynis_report_$TIMESTAMP.txt
echo "Lynis audit completed for $HOSTNAME" >> $LOG_DIR/security_log_$TIMESTAMP.log

# 3. Check for failed login attempts in /var/log/auth.log
grep "Failed password" /var/log/auth.log > $REPORT_DIR/failed_logins_$TIMESTAMP.txt
echo "Failed login attempts checked" >> $LOG_DIR/security_log_$TIMESTAMP.log

# 4. Scan for system updates (assuming Ubuntu/Debian-based)
apt update -y && apt upgrade -y > $REPORT_DIR/apt_updates_$TIMESTAMP.txt
echo "System update completed" >> $LOG_DIR/security_log_$TIMESTAMP.log

# 5. Intrusion Detection Check (via fail2ban or OSSEC)
systemctl status fail2ban > $REPORT_DIR/fail2ban_status_$TIMESTAMP.txt
echo "Fail2Ban status checked" >> $LOG_DIR/security_log_$TIMESTAMP.log

# 6. Send a consolidated report to the admin
REPORT_BODY="Security Scan Completed for $HOSTNAME:
- Nmap Scan: $(cat $REPORT_DIR/nmap_scan_$TIMESTAMP.txt | head -n 10)
- Lynis Audit: $(cat $REPORT_DIR/lynis_report_$TIMESTAMP.txt | head -n 10)
- Failed Logins: $(cat $REPORT_DIR/failed_logins_$TIMESTAMP.txt | head -n 10)
- System Updates: $(cat $REPORT_DIR/apt_updates_$TIMESTAMP.txt | head -n 10)
- Fail2Ban Status: $(cat $REPORT_DIR/fail2ban_status_$TIMESTAMP.txt | head -n 10)

For full reports, check the logs and reports on the server at $LOG_DIR and $REPORT_DIR."

# Send Email
send_email "Security Scan Report for $HOSTNAME - $TIMESTAMP" "$REPORT_BODY"

# Optional: You can also integrate Slack, Teams, or other notification systems here for alerts.

echo "Security Scan Report sent to $ADMIN_EMAIL"
