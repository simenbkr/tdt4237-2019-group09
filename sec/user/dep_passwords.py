from django.contrib.auth.hashers import MD5PasswordHasher

# this file is deprecated. Using argon2 instead
class CustomMD5PasswordHasher(MD5PasswordHasher):

    def salt(self):
        return "tdt4237"
