# Ficha de Personagem - Tormenta 20
# Character Sheet - Tormenta 20

[English version below](#english-version)

Uma aplicação web desenvolvida com Streamlit para criar e gerenciar fichas de personagem do sistema Tormenta 20.

## Funcionalidades

### Informações Básicas
- Nome, nível e raça do personagem
- Sistema de multiclasse
- Divindade e tendência
- Upload e exibição de imagem do personagem

### Atributos
- Força, Destreza, Constituição
- Inteligência, Sabedoria, Carisma
- Cálculo automático de modificadores

### Perícias
- Lista completa de perícias do T20
- Opção de marcar perícias treinadas
- Escolha do atributo base para cada perícia
- Cálculo automático de bônus

### Recursos
- Vida, Mana e Prana
- Barras de progresso visuais
- Recursos adicionais personalizáveis
- Cores personalizáveis para cada recurso

### Inventário
- Sistema de dinheiro (T$, PP, PO, PE, PC)
- Controle de carga
- Itens com propriedades detalhadas:
  - Nome, tipo, quantidade, peso e valor
  - Descrições e propriedades
  - Campos específicos para armas
  - Campos específicos para itens mágicos
  - Bônus em atributos
  - Bônus em perícias
  - Outros bônus (ataque, dano, defesa, iniciativa)

### Magias
- Organização por tipo (Arcana/Divina)
- Organização por nível (1º a 5º)
- Campos para:
  - Nome e escola
  - Execução, alcance e alvo
  - Duração e resistência
  - Descrição detalhada

### Poderes e Habilidades
- Nome e tipo
- Custo e requisitos
- Descrição detalhada

### Salvamento e Carregamento
- Exportação da ficha em formato JSON
- Importação de fichas salvas
- Preservação de todas as informações
- Suporte para imagem do personagem

## Requisitos

- Python 3.7+
- Streamlit
- Pillow (PIL)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
streamlit run app.py
```

## Uso

1. Acesse a aplicação no navegador (geralmente em http://localhost:8501)
2. Preencha as informações do personagem
3. Use o botão "Salvar Ficha" para exportar em JSON
4. Use o botão "Carregar Ficha" para importar uma ficha salva

## Recursos Técnicos

- Interface responsiva
- Atualização automática de cálculos
- Persistência de dados via JSON
- Suporte a imagens em base64
- Sistema de estados para preservar alterações

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:
1. Reportar bugs
2. Sugerir novas funcionalidades
3. Enviar pull requests

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

# English Version

A web application developed with Streamlit to create and manage character sheets for the Tormenta 20 system.

## Features

### Basic Information
- Character name, level, and race
- Multiclass system
- Deity and alignment
- Character image upload and display

### Attributes
- Strength, Dexterity, Constitution
- Intelligence, Wisdom, Charisma
- Automatic modifier calculation

### Skills
- Complete list of T20 skills
- Option to mark trained skills
- Choose base attribute for each skill
- Automatic bonus calculation

### Resources
- Life, Mana, and Prana
- Visual progress bars
- Customizable additional resources
- Customizable colors for each resource

### Inventory
- Money system (T$, PP, PO, PE, PC)
- Load management
- Items with detailed properties:
  - Name, type, quantity, weight, and value
  - Descriptions and properties
  - Specific fields for weapons
  - Specific fields for magical items
  - Attribute bonuses
  - Skill bonuses
  - Other bonuses (attack, damage, defense, initiative)

### Spells
- Organization by type (Arcane/Divine)
- Organization by level (1st to 5th)
- Fields for:
  - Name and school
  - Execution, range, and target
  - Duration and resistance
  - Detailed description

### Powers and Abilities
- Name and type
- Cost and requirements
- Detailed description

### Save and Load
- Character sheet export in JSON format
- Import saved character sheets
- Preservation of all information
- Character image support

## Requirements

- Python 3.7+
- Streamlit
- Pillow (PIL)

## Installation

1. Clone the repository:
```bash
git clone [REPOSITORY_URL]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Access the application in your browser (usually at http://localhost:8501)
2. Fill in the character information
3. Use the "Save Sheet" button to export as JSON
4. Use the "Load Sheet" button to import a saved sheet

## Technical Features

- Responsive interface
- Automatic calculation updates
- JSON data persistence
- Base64 image support
- State system to preserve changes

## Contributing

Contributions are welcome! Feel free to:
1. Report bugs
2. Suggest new features
3. Submit pull requests

## License

This project is under the MIT license. See the LICENSE file for more details. 