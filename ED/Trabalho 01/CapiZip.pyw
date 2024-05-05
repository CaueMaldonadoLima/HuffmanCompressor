#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from datetime import datetime
from configparser import ConfigParser
import locale
from os.path import exists, isfile, abspath
from time import time
from urllib.request import urlretrieve
from subprocess import Popen, PIPE

from tkinter import Tk, StringVar, filedialog, scrolledtext, TOP, LEFT, RIGHT, END, PhotoImage, Message, messagebox
from tkinter.ttk import Style, Frame, Entry, Button, Label
from tkinter.font import Font, BOLD, ITALIC


def gui():
    def procurar(titulo, tipos, var, deve_existir=False):
        if deve_existir:
            caminho = filedialog.askopenfilename(title=titulo, filetypes=tipos)
        else:
            caminho = filedialog.asksaveasfilename(title=titulo, filetypes=tipos, confirmoverwrite=False)
        if caminho:
            var.set(caminho)
            escrever_configuracao()
            define_estados_botoes()

    def define_estados_botoes():
        if not all((arquivo.get(), compactado.get(), executavel.get())):
            botao_comp.config(state='disabled')
            botao_descomp.config(state='disabled')
        else:
            botao_comp.config(state='normal')
            botao_descomp.config(state='normal')

    def ler_configuracao():
        CFG.read(arquivo_cfg)
        # Obtém seção (cria se não existe)
        secao = CFG.setdefault('CAPIZIP', {})
        # Define valores padrões vazios, caso falte algum
        for chave in VARS_CFG:
            if chave not in secao:
                secao[chave] = ''
        if not isfile(secao.get('executavel', '')):
            secao['executavel'] = ''
        if not secao.get('compactado', '').endswith('.huff'):
            secao['compactado'] = ''
        for chave, var in VARS_CFG.items():
            var.set(secao[chave])
        # Escreve configuração (caso algum padrão tenha sido definido)
        escrever_configuracao()

    def caminho_alterado(funcao_verificacao=None):
        if funcao_verificacao:
            funcao_verificacao()
        escrever_configuracao()
        define_estados_botoes()

    def verifica_compactado():
        caminho = VARS_CFG['compactado'].get()
        if caminho and not caminho.endswith('.huff'):
            VARS_CFG['compactado'].set('')
            messagebox.showerror(title='Valor inválido', message='Valor inválido para "Arquivo compactado"',
                                 detail='O arquivo deve ter extensão *.huff.')
            return False

    def verifica_executavel():
        caminho = VARS_CFG['executavel'].get()
        if caminho and not isfile(caminho):
            VARS_CFG['executavel'].set('')
            messagebox.showerror(title='Valor inválido', message='Valor inválido para "Arquivo executável"',
                                 detail='O arquivo não existe.')
            return False

    def escrever_configuracao():
        secao = CFG.setdefault('CAPIZIP', {})
        for chave, var in VARS_CFG.items():
            secao[chave] = var.get()
        with open(arquivo_cfg, 'w', encoding='utf-8') as f:
            CFG.write(f)

    def download_imagens():
        URL_BASE = 'https://www.facom.ufms.br/~diego/capizip/'
        ARQUIVOS = {'capizip.ico', 'capizip.png', 'capizip2.png'}
        for f in ARQUIVOS:
            if not exists(f):
                urlretrieve(URL_BASE + f, f)

    def executar(cmd):
        try:
            for saida in _executar(cmd):
                log_time(saida)
        except Exception as e:
            log_time('Erro de execução, verifique a mensagem abaixo:\n')
            for linha in str(e).splitlines(keepends=True):
                log_plain('    ' + linha)
            log_plain('\n')
            return False
        return True

    def _executar(cmd):
        log_time('Executando comando %s\n' % ' '.join(cmd))
        cmd[0] = abspath(cmd[0])
        inicio = time()
        processo = Popen(cmd, stdout=PIPE, universal_newlines=True)
        for linha_saida in iter(processo.stdout.readline, ''):
            yield linha_saida
        processo.stdout.close()
        codigo = processo.wait()
        fim = time()
        log_time('Processo finalizado com código %d em %.2f segundos\n' % (codigo, fim - inicio))

    def compactar():
        f = arquivo.get()
        comp = compactado.get()
        exe = executavel.get()
        log_time('Compactando %s -> %s\n' % (f, comp))
        if not isfile(f):
            messagebox.showerror(title='Valor inválido', message='Valor inválido para "Arquivo"',
                                 detail='O arquivo não existe.')
            log_time('Erro: arquivo de entrada não existe.\n')
            return
        if executar([exe, 'c', f, comp]):
            log_time('Pronto\n')

    def descompactar():
        f = arquivo.get()
        comp = compactado.get()
        exe = executavel.get()
        log_time('Descompactando %s -> %s\n' % (comp, f))
        if not isfile(comp):
            messagebox.showerror(title='Valor inválido', message='Valor inválido para "Arquivo compactado"',
                                 detail='O arquivo não existe.')
            log_time('Erro: arquivo de entrada não existe.\n')
            return
        executar([exe, 'd', comp, f])
        log_time('Pronto\n')

    def log_time(message):
        time = datetime.today().strftime('%c')
        log_plain('[%s] %s' % (time, message))

    def log_plain(message):
        LOG.config(state='normal')
        LOG.insert(END, message)
        LOG.config(state='disabled')
        LOG.see(END)

    download_imagens()
    app = Tk(className='CapiZip')
    app.title('CapiZip - Front-end para compactador/descompactador Huffman ')
    try:
        app.iconbitmap('capizip.ico')
    except:
        try:
            app.iconphoto(True, PhotoImage(file='capizip.png'))
        except:
            pass

    Style().configure('TButton', padding=5)
    CFG = ConfigParser()
    arquivo_cfg = 'capizip.cfg'

    arquivo = StringVar()
    compactado = StringVar()
    executavel = StringVar()
    tipostodos = (('Todos os arquivos', '*'), )
    tiposhuff = (('Arquivos Huffman', '*.huff'), )

    VARS_CFG = {'arquivo': arquivo, 'compactado': compactado, 'executavel': executavel}
    ler_configuracao()

    quadro_superior = Frame(app)
    quadro_superior.pack(side=TOP)

    quadro_foto = Frame(quadro_superior, width=200, height=200)
    quadro_foto.pack_propagate(False)
    quadro_foto.pack(side=RIGHT, padx=5, pady=5, fill='none', expand=False)
    imagem = PhotoImage(file='capizip2.png')
    rotulo = Label(quadro_foto, image=imagem)
    rotulo.pack(side=TOP)

    quadro_dados = Frame(quadro_superior)
    quadro_dados.pack(side=LEFT)

    quadro = Frame(quadro_dados)
    quadro.pack(side=TOP, padx=5, pady=5, fill='x', expand=True)
    fonte = Font(quadro, size=16, weight=BOLD)
    texto = Label(quadro, text='Seja bem-vindo CapiZip®!', font=fonte)
    texto.pack(side=TOP)
    fonte = Font(quadro, slant=ITALIC)
    texto = Label(quadro, text='Um front-end para compactadores/descompactadores Huffman', font=fonte)
    texto.pack(side=TOP)
    texto = Message(quadro, text='Localize os arquivos e o executável do compactador/descompactador, e então os '
                    'botões ficarão disponíveis.', justify='center')
    texto.pack(side=TOP, fill='x', expand=True)
    texto.bind("<Configure>", lambda event: texto.configure(width=event.width-10))

    quadro = Frame(quadro_dados)
    quadro.pack(side=TOP, padx=5, pady=5, fill='x', expand=True)
    Label(quadro, text='Arquivo:').pack(side=LEFT, padx=5)
    e = Entry(quadro, width=30, textvariable=arquivo)
    e.pack(side=LEFT, padx=5, fill='x', expand=True)
    e.bind('<FocusOut>', lambda event: caminho_alterado())
    Button(quadro, text='🗁 Procurar',
           command=lambda: procurar('Selecione um arquivo', tipostodos, arquivo)).pack(side=LEFT)

    quadro = Frame(quadro_dados)
    quadro.pack(side=TOP, padx=5, pady=5, fill='x', expand=True)
    Label(quadro, text='Arquivo compactado:').pack(side=LEFT, padx=5)
    e = Entry(quadro, width=30, textvariable=compactado)
    e.pack(side=LEFT, padx=5, fill='x', expand=True)
    e.bind('<FocusOut>', lambda event: caminho_alterado(verifica_compactado))
    Button(quadro, text='🗁 Procurar',
           command=lambda: procurar('Selecione um arquivo Huffman', tiposhuff, compactado)).pack(side=LEFT)

    quadro = Frame(quadro_dados)
    quadro.pack(side=TOP, padx=5, pady=5, fill='x', expand=True)
    Label(quadro, text='Compactador/descompactador:').pack(side=LEFT, padx=5)
    e = Entry(quadro, width=30, textvariable=executavel)
    e.pack(side=LEFT, padx=5, fill='x', expand=True)
    e.bind('<FocusOut>', lambda event: caminho_alterado(verifica_executavel))
    Button(quadro, text='🗁 Procurar',
           command=lambda: procurar('Arquivo executável compactador/descompactador', tipostodos, executavel, True)
           ).pack(side=LEFT)

    quadro = Frame(quadro_dados)
    quadro.pack(side=TOP, padx=5, pady=5, fill='none', expand=True)
    botao_comp = Button(quadro, text='Compactar', command=compactar)
    botao_comp.pack(side=LEFT, padx=5)
    botao_descomp = Button(quadro, text='Descompactar', command=descompactar)
    botao_descomp.pack(side=LEFT, padx=5)
    define_estados_botoes()

    quadro_log = Frame(app)
    quadro_log.pack(side=TOP, padx=5, pady=5, fill='both', expand=True)
    LOG = scrolledtext.ScrolledText(quadro_log, height=10)
    LOG.pack(side=LEFT, fill='both', expand=True)
    LOG.config(state='disabled')

    app.mainloop()


if __name__ == '__main__':
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR')
        except:
            pass
    gui()
