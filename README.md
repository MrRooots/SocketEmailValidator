# SocketEmailValidator
Simple script that will validate email address and check using sockets requests if that email exists
1) The script will validate the email form from input file using REGEX
2) Get all mx-servers of email using dns.resolver.resolve()
3) Using socket "bridge" will perform connect, HELO, MAIL FROM and RCPT TO requests
4) Create output.txt with results
