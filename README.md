Tesouro Direto Extrato
----------------------

Permite capturar os seus extratos do Tesouro Direto e salvá-los num arquivo csv, que poderá ser usado para fazer análises

## Quick Start

Instalar dependências (necessário ter instalado o [pipenv](https://docs.pipenv.org/)):

```sh
$ pipenv install
```

## Configurar os parâmetros

Você deve criar um arquivo .env com os parâmetros para captura dos extratos, conforme abaixo:

```
ANO_INICIAL='2010'
LOGIN_USUARIO='MeuUsuario'
SENHA_USUARIO='MinhaSenha' 
```

## Executar a captura dos extratos

```sh
$ pipenv shell
$ python main.py
```

Após o término da execução o arquivo [extrato_tesouro_direto.csv](extrato_tesouro_direto.csv) estará disponível e atualizado com os extratos.

O arquivo de saída terá o layout abaixo:

dt_referencia | corretora | titulo | dt_vencimento | vr_investido | vr_bruto | vr_liquido | qtd_total | qtd_bloqueado
------------- | --------- | ------ | ------------- | ------------ | -------- | ---------- | --------- | -------------
