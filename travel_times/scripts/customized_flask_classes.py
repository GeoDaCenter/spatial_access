from wtforms import SelectField, SelectMultipleField
import wtforms

class SelectFieldWithoutPreValidation(SelectField):

    def pre_validate(self, form):

        """
        The SelectField class's pre_validate function executes when the form is instantiated.  
        Most SelectField objects in forms.py are passed in an empty list for the choices attribute, and
        JavaScript is used to dynamically populate the list based on user inputs.  The form was not
        developed to detect such a change.  The SelectField class's pre_validate function sees that
        the choices list is empty, causing it to throw an Exception.  The pre_validate function has 
        been added to execute no code.  
        """

        return

class SelectMultipleFieldWithoutPreValidation(SelectMultipleField):
    
    def pre_validate(self, form):
        
        """
        The SelectMultipleField class's pre_validate function executes when the form is instantiated.  
        Most SelectMultipleField objects in forms.py are passed in an empty list for the choices attribute, and
        JavaScript is used to dynamically populate the list based on user inputs.  The form was not
        developed to detect such a change.  The SelectMultipleField class's pre_validate function sees that
        the choices list is empty, causing it to throw an Exception.  The pre_validate function has 
        been added to execute no code.  
        """

        return 
