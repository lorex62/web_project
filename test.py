import smtplib                                      # Импортируем библиотеку по работе с SMTP

# Добавляем необходимые подклассы - MIME-типы
from email.mime.multipart import MIMEMultipart      # Многокомпонентный объект
from email.mime.text import MIMEText                # Текст/HTML
from email.mime.image import MIMEImage              # Изображения

addr_from = "zxdszd@bk.ru"                 # Адресат
addr_to   = "ruw97490@bcaoo.com"                   # Получатель
password  = "AAyLP3su2vs-"                                  # Пароль

msg = MIMEMultipart()                               # Создаем сообщение
msg['From']    = addr_from                          # Адресат
msg['To']      = addr_to                            # Получатель
msg['Subject'] = 'Тема сообщения'                   # Тема сообщения

body = "Текст сообщения"
msg.attach(MIMEText(body, 'plain'))                 # Добавляем в сообщение текст

server = smtplib.SMTP('smtp-server', 587)           # Создаем объект SMTP
server.set_debuglevel(True)                         # Включаем режим отладки - если отчет не нужен, строку можно закомментировать
server.starttls()                                   # Начинаем шифрованный обмен по TLS
server.login(addr_from, password)                   # Получаем доступ
server.send_message(msg)                            # Отправляем сообщение
server.quit()                                       # Выходим