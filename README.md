# Análise Preditiva de um dataset de Pokémon

## Alunos: Eduardo da Maia Haak e Lukas Thiago Rodrigues

### Introdução ao Projeto

No mundo de Pokémon, cada pokémon tem diversos atributos que diferem entre uma espécie e outra a fim de torná-los únicos. A maioria dos atributos definem a força de um pokémon em batalha, enquanto outros determinam coisas referentes ao crescimento e variações cosméticas.

A fim de não explicar mecânicas que fazem parte dos RPGs desde os anos 70, basta saber que pokémon diferentes precisam de valores diferentes de pontos de experiência para subir de nível. Com base nisso, a pergunta que buscamos responder foi: "Quais são as relações entre tipos e status base, e o grupo de crescimento dos pokémon?".

Nossa intenção foi construir um modelo preditivo cujo objetivo é descobrir se há fatores dentro das demais características do pokémon que ditam essa velocidade de crescimento das criaturinhas.

Ao primeiro olhar, essa análise não parece ser muito útil para meras pessoas normais, porém, para aqueles que são viciados em pokémon, essa análise é importante para saber escolher quais são os melhores pokémons para escolher, porque nem sempre o que sobre de nível mais rápido é o mais forte.

### Os Dados

O dataset que a gente escolheu foi o "The Complete Pokemon Dataset" disponibilizado no Kaggle (https://www.kaggle.com/datasets/rounakbanik/pokemon), pois ele possui as variáveis necessárias para a nossa análise.
Foi definido que a arquitetura de armazenamento para esses dados será o Data Lake, pois os dados não estão muito poluídos, além de que são dados públicos. Fora que o Data Lake permite armazenar dados em diferentes formatos de forma econômica e flexível, além de que ele se encaixa bem como ambiente para armazenar tanto os dados brutos quanto versões pré-processadas que serão consumidas posteriormente nos modelos de predição.

#### Pipeline:
  - Para começar, exportamos os dados em um relatório csv (pokemon.csv), depois criamos um algoritmo para inspecionar os dados:

    <img width="554" height="489" alt="image" src="https://github.com/user-attachments/assets/5416c238-b077-4baf-b7e9-b60aa2c0cc39" />

    <img width="1515" height="348" alt="image" src="https://github.com/user-attachments/assets/37e7fb4c-60fc-4c00-8520-36a894789d43" />


  - Depois disso, fizemos um outro tratamento para manter apenas as colunas que iríamos utilizar para essa análise:

    <img width="965" height="542" alt="image" src="https://github.com/user-attachments/assets/f318130b-2e9b-4194-8d69-3606e027f7e2" />

    <img width="1576" height="234" alt="image" src="https://github.com/user-attachments/assets/dcbd9e93-4d41-4a27-9673-52da6331d08f" />


  - Com uma análise mais profunda, identificamos que o pokémon "Minior" tinha 2 valores diferentes na coluna "capture_rate", um valor para cada forma. Então, filtramos por esse pokémon, duplicamos a linha, criamos uma nova coluna chamada "form", onde terá valor preenchido caso o pokémon tenha uma forma alternativa. Atribuímos os valores corretos para cada forma e então adicionamos novamente ao dataset:

    <img width="711" height="699" alt="image" src="https://github.com/user-attachments/assets/f922dc3d-0d80-4806-85c0-459dc6162b4f" />

  - Acontece que, além do "Minior", diversos Pokémon possuem variações de formas. Acontece que o Dataset original não lida muito bem com isso, então decidimos fazer um script robusto para incrementar o dataset com todas as variações, desde que elas apresentam alguma mudança em questão dos stats e tipos. Ele demora uns 6 minutos pra rodar, mas funciona, e é importante ter essas variações pois elas são valiosas para o balanceamento do jogo nas gerações 7 para cima. O código é muito grande para colar de uma só vez, então vai ser quebrado em partes:
    - Buscamos os dados de todos os pokémon através da pokeapi, busca por um em específico e retorna o conteúdo:
    
      <img width="818" height="546" alt="image" src="https://github.com/user-attachments/assets/3b346217-38a8-4991-94b0-399d84365524" />

    - Converte a taxa de crescimento e o nome das gerações para número:
      
      <img width="1003" height="650" alt="image" src="https://github.com/user-attachments/assets/fde8cf8b-b420-461b-b0e3-a0982c6dd9d2" />

    - Extrai os "stats" e os "types" de um pokémon:

      <img width="1505" height="588" alt="image" src="https://github.com/user-attachments/assets/f4995214-e331-462b-9a7d-006faecf1c29" />

    - Verifica se as informações são as mesmas, se não forem, gera uma forma nova para o pokémon:

      <img width="1143" height="421" alt="image" src="https://github.com/user-attachments/assets/1bcda8a4-5548-4b73-82fa-c74148999487" />

    - Função principal, que chama todos esses outros métodos acima através da função "enrich_with_pokeapi":

      <img width="800" height="698" alt="image" src="https://github.com/user-attachments/assets/12fd4fd0-86b6-4b15-8c7f-2dd1d0d0eaad" />

    - Ao final de tudo, é salvo em um novo arquivo: "pokemon_finalizado.csv".






