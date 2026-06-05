from app import app
from waitress import serve  

if __name__ == '__main__':
    print("Servidor Itemizer iniciado com sucesso na rede local na porta 5000...")
    # host='0.0.0.0' faz o Flask escutar todas as interfaces de rede local
    serve(app, host='0.0.0.0', port=5000, threads=6)