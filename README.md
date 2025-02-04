# Youtube Video Downloader

Este projeto é uma aplicação de download de vídeos do youtube usando `yt-dlp` e `tkinter` para a interface gráfica. A aplicação permite que o usuário selecione uma pasta para salvar os vídeos e acompanhe o progresso do download.

## Instalação

1. Clone o repositório do GitHub:

    ```sh
    git clone https://github.com/VitorTinelli/youtube-video-dowloader.git
    cd VideoDownloader
    ```

2. Instale as dependências:

    ```sh
    pip install -r requirements.txt
    ```

## Uso

1. Execute a aplicação:

    ```sh
    python main.py
    ```

2. Na interface gráfica, clique no botão "URL" para abrir uma nova janela onde você pode inserir a URL do vídeo.

3. Clique no botão "Submit" para iniciar o download. A barra de progresso mostrará o andamento do download.

## Estrutura do Projeto

- [main.py](http://_vscodecontentref_/1): Arquivo principal que inicializa a interface gráfica.
- [menu.py](http://_vscodecontentref_/2): Define o menu da aplicação e gerencia a seleção da pasta.
- [baixarVideo.py](http://_vscodecontentref_/3): Contém a lógica para baixar vídeos usando `yt-dlp`.
- [configurations.json](http://_vscodecontentref_/4): Arquivo de configuração para definir o caminho da pasta, qualidade do vídeo e template de saída.

## Contribuição

1. Faça um fork do projeto.
2. Crie uma nova branch (`git checkout -b feature/nova-feature`).
3. Faça commit das suas alterações (`git commit -am 'Adiciona nova feature'`).
4. Faça push para a branch (`git push origin feature/nova-feature`).
5. Abra um Pull Request.
