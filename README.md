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


#### Análise Exploratória:

Para nos ajudar a entender os nossos dados, realizamos a análise exploratória deles considerando como variável-alvo a coluna *experience_growth*, e os gráficos gerados acabou nos mostrando algumas coisas interessantes:

  - A primeira análise que fizemos, foi para buscar em qual grupo de crescimento (*experience_growth*) a maioria dos pokémon se encontram:

    <img width="854" height="551" alt="image" src="https://github.com/user-attachments/assets/3fb4989b-bd2c-4ed6-b565-4f1fd541b2de" />

    Com isso observamos que a maioria dos pokémon estão concentrados na metade, o que representa os grupos *medium-slow* e *medium-fast*. Isso é esperado, já que existem muitos pokémon "medianos" em força. Mesmo assim, pode-se observar uma discrepância entre os grupos *medium-slow* e *medium-fast*, em que o segundo tem quase o dobro de ocorrências do que o primeiro.

  - Em seguida, começamos a cruzar variáveis para encontrar relações que nos ajudem a responder nossa pergunta. Nossa primeira hipótese é que *base_total* influencia *experience_growth*:

    <img width="849" height="552" alt="image" src="https://github.com/user-attachments/assets/d3d60e6e-aea4-410e-9cec-82e154312d79" />

    O boxplot acima revela claramente uma constância, quanto maior o status, maior é o grupo de expêriencia. A única categoria a apresentar outliers é *slow* (1250000) e isso provavelmente se deve ao fato de haverem pré-evoluções do pokémon muito fortes mas que não são tão fortes antes de evoluir. Isso é perceptível pela presença de pokémon com status base baixos em todas as categorias. Outras anomalias são as categorias *erratic* (600000) e *fluctuating* (1640000) que apesar de suas posições nos gráficos, na verdade são as categorias mais lenta de level up e mais rápida, respecivamente. O motivo delas terem quantidades de xp totais não condizentes é por que elas compensam sua velocidade/lentidão nos últimos níveis (level 90 - 100), onde elas se tornam o oposto da velocidade que elas tinham anteriormente. Além disso, esses dois grupos apresentam poucos membros, o que dificulta a realização de uma análise objetiva.

  - Para entender melhor se existem outras variáveis que afetam *experience_growth*, decidimos utilizar um heatmap com todas as variáveis numéricas presentes no modelo:

    <img width="1034" height="957" alt="image" src="https://github.com/user-attachments/assets/b3001c1e-a145-47bb-b093-35504c1258c2" />

    Com esse heatmap, podemos observar que ele mostra o oposto do que foi visto anteriormente, aqui está mostrando que *base_total* tem uma correlação fraca com *capture_rate*, enquanto o antes mostrava o contrário. Outro ponto a se observar, é que o *base_total* também não tem correlação com o *capture_rate*, indo contra o que estávamos pensando. Agora, se tratando de correlações fortes, o gráfico nos mostra que existe uma entre *generation* e *pokedex_number*, o que não é nem um pouco surpreendente já que a cada geração os números incrementam de onde pararam na geração anterior. Outras correlações esperadas são *sp_attack*, *attack*, *sp_defense*, *hp*, *defense* e *speed* contribuindo para *base_total*, embora seja interessante ver os pesos, significando que há mais pokémon com ataque especial alto do que velocidade. Além disso *is_legendary* tem uma correlação relativamente alta com *base_total*, o que também faz sentido e é até meio estranho que não seja maior. Além desse gráfico, nós experimentamos computar pokémon de cada geração individualmente mas os gráficos ficaram praticamente idênticos, variando muito pouco entre os números, mas mostrando que há sim algum tipo de balanceamento ou padronização intencional entre cada adição de criaturas.

  - Resolvemos também fazer uma relação entre a taxa de captura e o status total, separado em grupos pelo grupo de crescimento:

    <img width="1009" height="630" alt="image" src="https://github.com/user-attachments/assets/c1ab1cb3-3ec3-46cf-891c-17e2c8339ea7" />

    Esse gráfico de dispersão mostra que existem pokémon com status base altos que são que são bem fáceis de capturar, e isso faz sentido, pensando que alguns deles são eventos scriptados pelo próprio jogo. Outras informações que podemos extraír pelas cores são que: os grupos de experiência mais lentos tendem a se concentrar dentre os mais difíceis de capturar e os grupos erratic e fluctuating se fazem presentes em quase todos os quadrantes. Além disso, pode-se observar a relação óbvia de que pokémon mais fortes são em geral mais difíceis de capturar. O gráfico aparenta ter uma quantidade elevada de outliers, mas isso pode ser explicado através de decisões de design que não necessáriamente tem a ver com os atributos sendo analizados, mas sim outras características únicas que não se podem ser quantificadas da forma que fizemos com os atributos. O importante é que a tendência é tangível.


Com base em todas essas análise, podemos concluir que:
   - A maioria dos pokémon se encontra nos grupos de crescimento intermediários (*medium-fast* e *medium-slow*);
   - Quanto maior o *base_total* do pokémon, maior é a quantidade de *experience_growth* necessária para atingir o nível máximo;
   - *experience_growth* não parece ser tão afetado por algum atributo individualmente, mas está na meio de outras relações entre multiplos atributos, mostrando que sua tendência é uma das duas: complicada ou inexistente.
   - As variáveis mais promissoras para incluir em um modelo preditivo para 'experience_growth' são:
       - *base_total* - Devido à sua forte correlação mostrada no boxplot além de ter uma forte correlação com outras variáveis, como a *is_legendary* por exemplo;
       - *capture_rate* - Porque suas relações com as demais variaveis revelam mais sobre as tendências do *experience_growth*, além da relação entre as duas;
       - *is_legendary* - Apresente uma correlação forte com *experience_growth*, pelo menos de acordo com o heatmap.
