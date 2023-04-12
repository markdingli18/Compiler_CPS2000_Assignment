import PixArLang

while True:
    text = input('PixArLang > ')
    result, error = PixArLang.run('<stdin', text)
    
    if error: 
        print(error.as_string())
    else: 
        print(result)