import socket
import random
import re
import dns
from dns import resolver

EMAIL_REGEX = r"^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$"
CODES = {
  0: 'Domain doesn\'t exist',
  1: 'Email exist',
  2: 'Some errors during connections',
}
EMAILS = []


def get_emails_from_file(filename):
  try:
    with open(filename if filename else 'email.txt', 'r') as file:
      global EMAILS
      EMAILS = [e_mail.strip() for e_mail in file]
  except FileNotFoundError:
    print(f'No file {filename} in the directory!')


def is_valid_email(email_addr):
  return re.search(EMAIL_REGEX, email_addr)


def get_domains(email_addr):
  try:
    return [str(i).split(' ')[1][:-1] for i in resolver.resolve(email_addr.split('@')[1], 'MX')]
  except dns.exception.DNSException as error:
    print(f'Error during dns resolving: {error}!')
    return None


def main(email_addr, domain_address):
  if not is_valid_email(email_addr):
    return 0

  local_addr = ('0.0.0.0', random.randint(5000, 8001))
  print(f'Checking {email_addr} by local port {local_addr[1]} on {domain_address} domain')

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as local_socket:
    local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    local_socket.setblocking(False)
    local_socket.bind(local_addr)
    local_socket.settimeout(5)

    try:
      local_socket.connect((domain_address, 25))
      print(f'Local socket connected!')

      answer = local_socket.recv(256).decode()[0:3]
      print('Making CONNECT request \t=>\t', end='')

      if answer == '220':
        print(answer)
        print('Making HELO request    \t=>\t', end='')

        local_socket.sendall('HELO asusmrk.gmail.com\n'.encode())
        try:
          answer = local_socket.recv(256).decode()[0:3]
        except socket.error as error:
          print(f'Error during first (HELO) data receiving: {error}')
          return 2, error

        print(answer, end='')
        print('\nMaking MAILFROM request\t=>\t', end='')

        local_socket.sendall('MAIL FROM: <asusmrk@gmail.com>\n'.encode())
        try:
          answer = local_socket.recv(256).decode()[0:3]
        except socket.error as error:
          print(f'Error during second (MAIL FROM) data receiving: {error}')
          return 2, error

        print(answer, end='')
        print('\nMaking RCPTTO request\t=>\t', end='')

        local_socket.sendall(f'RCPT TO: <{email_addr}>\n'.encode())
        try:
          answer = local_socket.recv(256).decode()[0:3]
        except socket.error as error:
          print(f'Error during third (RCPT TO) data receiving: {error}')
          return 2, error

        print(answer)

        return int(answer == '250'), None
      else:
        return 0, None

    except socket.error as error:
      print(f'Error during connection! Error: {error}')
      return 2, error
    finally:
      local_socket.close()


if __name__ == '__main__':
  print('-'*88 + '\nYou are running the program that will validate email address and check if that one exist\n' + '-'*88)
  get_emails_from_file(input('Enter a filename (leave blank for email.txt): '))

  if EMAILS:
    with open('output.txt', 'w') as file:
      max_email_length = max(map(len, EMAILS))

      for email in EMAILS:
        domains = get_domains(email)

        if domains:
          for domain in domains:
            result, code = main(email, domain)

            if result == 1:
              file.write(f'{email}{" "*(max_email_length - len(email))}\t=> Email exist!\n')
              break
            if result == 2:
              file.write(f'{email}{" "*(max_email_length - len(email))}\t=> {code}!\n')
            if not result:
              file.write(f'{email}{" "*(max_email_length - len(email))}\t=> Email does not exist!\n')
              break
        else:
          file.write(f'{email}{" "*(max_email_length - len(email))}\t=> Error during dns resolving!\n')

  input('Press any button to exit...')
