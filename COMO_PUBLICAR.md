# Como publicar seu site (grátis, em ~5 minutos)

## Passo 1 — Criar conta na Vercel
1. Acesse https://vercel.com
2. Clique em "Sign Up" e entre com seu e-mail ou conta do Google (não precisa cartão de crédito).

## Passo 2 — Publicar o site
1. Depois de logado, clique em "Add New..." → "Project".
2. Escolha a opção de enviar uma pasta (drag and drop) — pode arrastar a pasta deste projeto (a mesma que veio dentro do .zip, já descompactada) direto para a área indicada.
3. Clique em "Deploy". Em menos de 1 minuto o site estará no ar.

## Passo 3 — Escolher o nome do endereço
1. Dentro do projeto na Vercel, vá em "Settings" → "Domains".
2. Você verá um endereço padrão tipo `dorgivalneto-imoveis-xxxx.vercel.app`.
3. Clique em "Edit" e troque para `dorgivalneto-imoveis` — o endereço final fica `dorgivalneto-imoveis.vercel.app`.

## Passo 4 — Configurar seu WhatsApp real
Antes de publicar (ou depois, republicando), abra o arquivo `assets/data.js` e troque:
```
whatsapp: "5583999999999"
```
pelo seu número real, com DDI 55 e sem espaços/traços (ex: `5583988887777`).

## Como atualizar depois de publicado
Sempre que quiser adicionar, editar ou remover um imóvel, me chame aqui no chat com os dados (ou fotos) do imóvel. Eu atualizo o arquivo `assets/data.js` e te devolvo os arquivos atualizados — você só precisa repetir o Passo 2 (arrastar a pasta atualizada de novo na Vercel, ou usar "Redeploy" caso já tenha conectado a um repositório do GitHub).

## Alternativa mais avançada (opcional, para o futuro)
Se quiser conectar direto ao GitHub (para eu poder empurrar atualizações automaticamente sem você precisar arrastar pastas), me avise — configuramos isso quando fizer sentido para você.
