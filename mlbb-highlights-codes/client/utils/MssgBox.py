from CTkMessagebox import CTkMessagebox

class MessageBox():
    def show_info(mssg_title, mssg):
        CTkMessagebox(title=mssg_title, message= mssg)

    def show_checkmark(mssg_title, mssg):
        CTkMessagebox(message=mssg,
                    icon="check")
        
    def show_error(mssg_title, mssg):
        msg = CTkMessagebox(title=mssg_title, message=mssg, icon="cancel")
        response = msg.get()
        if response == "OK":
            return True
    
    def ask_question(mssg_title, mssg):
        msg = CTkMessagebox(title=mssg_title, message=mssg,
                            icon="question", option_1="Cancel", option_2="No", option_3="Yes")
        response = msg.get()
        
        if response=="Yes":
            return response == "Yes" 
        else:
            print("Click 'Yes' to exit!")
        CTkMessagebox(title="Error", message=mssg, fg_color="#EBEBEB",
                      bg_color="#F0F4F7", font=("Poppins Medium", 13))
