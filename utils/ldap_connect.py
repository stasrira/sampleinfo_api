import ldap
import os
import traceback


class LdapConnect():
    def __init__(self, mlogObj = None):
        self.connect = None
        self.connected = False
        self.log = mlogObj

        # working user connection: 'CN=Service\, SealfonLab,CN=Managed Service Accounts,DC=mssmcampus,DC=mssm,DC=edu'
        ldap_user = os.environ.get('ST_LDAP_USER')
        ldap_pwd = os.environ.get('ST_LDAP_PWD')
        self.ldap_uri = os.environ.get('ST_LDAP_URI')

        # memberOf_required = os.environ.get('ST_LDAP_USER_MEMBER_OF')

        try:
            # connect and login to the ldap server
            self.connect = ldap.initialize(self.ldap_uri)
            result, error = self.login_to_ldap(self.connect, ldap_user, ldap_pwd)
            if result and error is None:
                self.connected = True
            else:
                if error and isinstance(error, tuple):
                    _str = 'Unexpected Error "{}" occurred during login to the LDAP server.\n{}'\
                        .format(error[0], error[1])
                    if self.log:
                        self.log.critical(_str)
                    raise error[0]
                else:
                    _str = 'Undefined Error occurred during login to the LDAP server.' \
                        .format(error[0], error[1])
                    if self.log:
                        self.log.critical(_str)

        except Exception as ex:
            _str = 'Unexpected Error "{}" occurred during during connecting to the LDAP server.\n{}'. \
                format(ex, traceback.format_exc())
            if self.log:
                self.log.critical(_str)
            raise ex

    def login_to_ldap(self, ldap_connect, ldap_user, ldap_pwd):
        try:
            # login to the ldap server
            ldap_connect.set_option(ldap.OPT_NETWORK_TIMEOUT, 10.0)
            ldap_connect.simple_bind_s(ldap_user, ldap_pwd)
            return True, None
        except Exception as ex:
            return False, (ex, traceback.format_exc())

    def validate_member_of_assignment(self, email, member_of_name_to_match):
        has_access = False
        result = self.connect.search_s('DC=mssmcampus,DC=mssm,DC=edu',
                                  ldap.SCOPE_SUBTREE,
                                  'mail={}'.format(email),
                                  ['memberOf'])
        if result and len(result) > 0 and len(result[0]) > 1 and 'memberOf' in result[0][1]:
            member_of = result[0][1]['memberOf']  # get memberOf list of items
            for member in member_of:
                items = str(member).split(',')
                for item in items:
                    value = str(item).split('=')[1]
                    if str(value) == member_of_name_to_match:  # '!!researchsan02a!shr1!neurology!Sealfon_Lab\\\\#rw'
                        # print('OK => has access to J drive; {}'.format(value))
                        has_access = True

        return has_access

    def validate_user_existence(self, email):
        user_exists = False
        result = self.connect.search_s('DC=mssmcampus,DC=mssm,DC=edu',
                                  ldap.SCOPE_SUBTREE,
                                  'mail={}'.format(email),
                                  ['cn'])
        if result:
            user_exists = True

        return user_exists

    def validate_user_credentials_by_email(self, email, pwd):
        # create temporary ldap connection to validate login details of the user
        connect_loc = ldap.initialize(self.ldap_uri)
        if email and pwd:
            result, error = self.login_to_ldap(connect_loc, email, pwd)
            if result:
                # login was successful
                return True, None
            else:
                # wrong login credentials
                return False, 'Wrong credentials'
        else:
            # an email address or a password were not provided
            return False, 'One or both of the provided credentials were invalid'

