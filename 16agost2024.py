from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.clock import Clock
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr

__version__ = "1.0.0"

def iniciar_vox(mic, recognizer, chat, engine=None):
    recognizer.energy_threshold = 300  # Ajuste conforme necessário
    print("Detector de som ativado...")

    while True:
        with mic as fonte:
            recognizer.adjust_for_ambient_noise(fonte)
            print("Aguardando som...")
            audio = recognizer.listen(fonte, timeout=None, phrase_time_limit=10)

            # Verifica se captou algum som
            if audio:
                print("Som detectado, iniciando reconhecimento de fala...")
                try:
                    texto = recognizer.recognize_google(audio, language="pt-BR")
                    print("Você disse: {}".format(texto))
                    
                    if texto.lower() == "desligar":
                        print("Encerrando detector de som...")
                        break

                    if texto.strip():
                        response = chat.send_message(texto)
                        print("Geraldo:", response.text, "\n")
                        if engine:
                            engine.say(response.text)
                            engine.runAndWait()
                    else:
                        print("Texto capturado está vazio. Nenhuma mensagem foi enviada para a IA.")

                except Exception as e:
                    print("Erro no reconhecimento de fala:", e)
            else:
                print("Nenhum som detectado. Continuando monitoramento...")

def main():
    assistente_falante = True
    ligar_microfone = True

    genai.configure(api_key="AIzaSyAWDtYtY8rIasca_hUmatpXggRbreccER8")
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])

    if assistente_falante:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('rate', 180)

        voz = 58
        engine.setProperty('voice', voices[voz].id)
    else:
        engine = None

    if ligar_microfone:
        r = sr.Recognizer()
        mic = sr.Microphone()

        iniciar_vox(mic, r, chat, engine)
    else:
        print("Microfone desligado, saída manual não implementada neste modo.")

class MyApp(App):

    def build(self):
        # Layout principal
        layout = BoxLayout(orientation='vertical')

        # Adicionando o papel de parede
        bg = Image(source='1000022325-01.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(bg)

        # Layout para o log e o botão
        log_and_button_layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10])
        
        # Log de terminal
        self.log_label = Label(size_hint_y=None, height=400, text='Log de Terminal\n')
        scroll_view = ScrollView(size_hint=(1, None), size=(400, 300))
        scroll_view.add_widget(self.log_label)
        log_and_button_layout.add_widget(scroll_view)

        # Botão Start/Stop
        self.start_stop_button = Button(text='Start', size_hint_y=None, height=50)
        self.start_stop_button.bind(on_press=self.toggle_start_stop)
        log_and_button_layout.add_widget(self.start_stop_button)

        # Adicionando o layout do log e botão ao layout principal
        layout.add_widget(log_and_button_layout)
        
        return layout

    def toggle_start_stop(self, instance):
        if self.start_stop_button.text == 'Start':
            self.start_stop_button.text = 'Stop'
            self.add_to_log('Iniciando...')
            main()
            # Adicione aqui o código para iniciar o seu processo
            
        else:
            self.start_stop_button.text = 'Start'
            self.add_to_log('Parando...')
            # Adicione aqui o código para parar o seu processo

    def add_to_log(self, message):
        self.log_label.text += f'{message}\n'
        # Atualiza o scroll para o final do log
        Clock.schedule_once(self.update_scroll, 0.1)

    def update_scroll(self, dt):
        self.log_label.height = max(self.log_label.texture_size[1], self.log_label.height)
        self.log_label.parent.scroll_to(self.log_label)
 
if __name__ == '__main__':
    MyApp().run()
