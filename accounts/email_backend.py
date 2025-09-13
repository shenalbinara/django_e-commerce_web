from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend

class CustomEmailBackend(DjangoEmailBackend):
    def open(self):
        if self.connection:
            return False
        connection_class = self.connection_class
        try:
            self.connection = connection_class(self.host, self.port, timeout=self.timeout)
            if self.use_tls:
                self.connection.starttls()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception:
            if self.fail_silently:
                return False
            raise
