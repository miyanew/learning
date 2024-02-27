#!/bin/bash

# Set a log file
LOGFILE="/tmp/${0%.sh}.log"

# Reset the log file
echo "" > $LOGFILE

# Function to write to log file
log_message() {
    echo "$1" >> $LOGFILE
}

# Function to display console messages
console_message() {
    flg="${2:-n}"
    str=$1
    if [ $flg == 1 ]; then
        str="$1\n"
    fi
    echo -e $str
    echo -e "\n----> $1 <----\n" >> $LOGFILE
}

# Function to execute command and log messages
execute_and_log() {
    log_message "Executing: $1"
    eval $1 >> $LOGFILE 2>&1
    status=$?
    if [ $status -ne 0 ]; then
        echo "Error: '$1' failed with status $status. Check $LOGFILE."
        exit 1
    fi
    return $status
}

# Function to execute command and log messages and stdout
execute_and_log_o() {
    log_message "Executing: $1"
    output=$(eval $1 2>&1)
    status=$?
    echo "$output"
    echo "$output" >> $LOGFILE
    if [ $status -ne 0 ]; then
        echo "Error: '$1' failed with status $status. Check $LOGFILE."
        exit 1
    fi
    return $status
}

# Function to exectute and log messages with progress indicator
execute_and_log_with_progress() {
    log_message "Executing: $1"
    eval $1 >> $LOGFILE 2>&1 &
    pid=$!
    progress_indicator=('|' '/' '-' '|')
    index=0

    while kill -0 $pid 2> /dev/null; do
        echo -ne "${progress_indicator[$index]} Command is still running...\r"
        sleep 1
        let "index = (index + 1) % 4"
    done
    echo ""
    wait $pid
    status=$?
    if [ $status -ne 0 ]; then
        echo "Error: '$1' failed with status $status. Check $LOGFILE."
        exit 1
    else
        echo "" >> $LOGFILE
    fi
    return $status
}

# Function to display progress messages
progress_message() {
    echo "========================================================" | tee -a $LOGFILE
    echo $1 | tee -a $LOGFILE
    echo "========================================================" | tee -a $LOGFILE
}

# Update Ubuntu
progress_message "Updating Ubuntu... (This may take some time...)"
execute_and_log "sudo hwclock --hctosys"
execute_and_log_with_progress "sudo ping -c 2 8.8.8.8"
console_message "Checked internet connectivity. (Step 1/3)"
execute_and_log_with_progress "sudo apt-get update -y"
console_message "Updated Ubuntu. (Step 2/3)"
execute_and_log_with_progress "DEBIAN_FRONTEND=noninteractive sudo apt-get upgrade -y"
console_message "Upgraded Ubuntu. (Step 3/3)" 1

# Install rbenv
progress_message "Installing rbenv... (This may take some time...)"
execute_and_log_with_progress "curl -fsSL https://github.com/rbenv/rbenv-installer/raw/HEAD/bin/rbenv-installer | bash"
console_message "Ran the installer."
execute_and_log "echo '' >> ~/.bashrc"
execute_and_log "echo '# rbenv configuration' >> ~/.bashrc"
execute_and_log "echo 'export PATH=\"$HOME/.rbenv/bin:$PATH\"' >> ~/.bashrc"
execute_and_log "echo 'eval \"\$(~/.rbenv/bin/rbenv init - bash)\"' >> ~/.bashrc"
execute_and_log "source ~/.bashrc"
source ~/.bashrc
execute_and_log "echo '' >> ~/.bash_profile"
execute_and_log "echo '# rbenv configuration' >> ~/.bash_profile"
execute_and_log "echo 'export PATH=\"$HOME/.rbenv/bin:$PATH\"' >> ~/.bash_profile"
execute_and_log "echo 'eval \"\$(~/.rbenv/bin/rbenv init - bash)\"' >> ~/.bash_profile"
execute_and_log "source ~/.bash_profile"
source ~/.bash_profile
execute_and_log "export PATH=\"$HOME/.rbenv/bin:$PATH\""
console_message "Updated bash configuration."
console_message "Installed rbenv." 1

# Install dependencies for ruby-build
progress_message "Installing dependencies for ruby-build... (This may take some time...)"
execute_and_log_with_progress "sudo apt-get install autoconf patch build-essential rustc libssl-dev libyaml-dev libreadline6-dev zlib1g-dev libgmp-dev libncurses5-dev libffi-dev libgdbm6 libgdbm-dev libdb-dev uuid-dev -y"
console_message "Installed dependencies for ruby-build." 1

# Select the specified Ruby version
console_message "Enter the Ruby version you want to install."
execute_and_log_o "rbenv install -l"
execute_and_log_o "echo -n :"
execute_and_log "read RB_VERSION"

# Install the specified Ruby version
progress_message "Installing Ruby...(This may take some time...)"
execute_and_log_with_progress "rbenv install $RB_VERSION"
execute_and_log "rbenv global \"$RB_VERSION\""
execute_and_log "RB_VERSION=$(ruby -v | cut -d' ' -f2)"
console_message "Applied Ruby -> $RB_VERSION"
console_message "Installed Ruby." 1
