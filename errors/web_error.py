from .entity_error import EntityErrors


class WebError(EntityErrors):

    def __init__(self, process_name, mcfg = None, mlog = None):
        self.mcfg = mcfg
        self.mlog = mlog
        EntityErrors.__init__(self, process_name)

    def get_errors_to_str(self):
        err_lst = []
        for er in self.get_errors():  # EntityErrors.get_errors
            # print ('er.error_desc = {}'.format(er.error_desc))
            err_lst.append({'error_desc': er.error_desc, 'error_number': er.error_number})

        error = {
            'process': str(self.entity),
            'errors': err_lst  # EntityErrors.get_errors(self)
        }
        return error

    def send_email(self, error_desc, error_number):
        from utils import send_email as email
        import traceback
        # print ('send email from error!!!')
        if self.mcfg:
            # send notification email alerting about the error
            email_subject = self.mcfg.get_value('Email/email_subject')
            email_body = 'Application: {}\nError message: {}\nError number: {}' \
                .format(self.mcfg.get_value('Email/application_id'), error_desc, error_number)
            try:
                email.send_yagmail(
                    emails_to=self.mcfg.get_value('Email/sent_to_emails'),
                    subject=email_subject,
                    message=email_body
                    # ,attachment_path = email_attchms_study
                )
            except Exception as ex:
                # report unexpected error during sending emails to a log file and continue
                _str = 'Unexpected Error "{}" occurred during an attempt to send an email.\n{}'. \
                    format(ex, traceback.format_exc())
                if self.mlog:
                    self.mlog.critical(_str)
