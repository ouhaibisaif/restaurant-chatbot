RESTAURANT = {
    "name": "Le Jardin Bleu",
    "address": "24 Rue des Oliviers, Tunis 1002, Tunisia",
    "phone": "+216 71 555 010",
    "email": "hello@lejardinbleu.local",
    "languages": ["English", "French", "Arabic"],
    "opening_hours": {
        "Monday": "11:00-23:00",
        "Tuesday": "11:00-23:00",
        "Wednesday": "11:00-23:00",
        "Thursday": "11:00-23:00",
        "Friday": "11:00-23:30",
        "Saturday": "11:00-23:30",
        "Sunday": "Closed",
    },
    "delivery": {
        "available": True,
        "hours": "12:00-22:00 Monday to Saturday",
        "areas": ["Tunis Centre", "Lac 1", "Lac 2", "Marsa"],
        "minimum_order": 25,
        "fee": 5,
    },
    "popular_dishes": [
        "Sea Bass with Lemon Couscous",
        "Vegetarian Pasta",
        "Harissa Honey Chicken",
    ],
    "faqs": [
        {
            "question": "Do you accept card payments?",
            "answer": "Yes, we accept cash, bank cards, and local mobile payment apps.",
        },
        {
            "question": "Do you have vegetarian options?",
            "answer": "Yes, vegetarian pasta, grilled vegetable plate, vegan salad, and brik with herbs are vegetarian.",
        },
        {
            "question": "Is reservation required?",
            "answer": "Walk-ins are welcome, but reservations are recommended for Friday and Saturday evenings.",
        },
        {
            "question": "Do you offer delivery?",
            "answer": "Yes, delivery is available from 12:00 to 22:00 Monday to Saturday in selected Tunis areas.",
        },
    ],
}


MENU = [
    {
        "category": "Starters",
        "items": [
            {
                "name": "Brik with Herbs",
                "description": "Crispy pastry with egg, parsley, potato, and capers.",
                "price": 9,
                "allergens": ["egg", "gluten"],
                "tags": ["vegetarian", "popular"],
            },
            {
                "name": "Vegan Salad",
                "description": "Seasonal greens, dates, almonds, citrus dressing.",
                "price": 12,
                "allergens": ["tree nuts"],
                "tags": ["vegan", "vegetarian"],
            },
            {
                "name": "Tunisian Mezze",
                "description": "Assorted olives, mechouia, hummus, and warm bread.",
                "price": 16,
                "allergens": ["sesame", "gluten"],
                "tags": ["sharing"],
            },
        ],
    },
    {
        "category": "Mains",
        "items": [
            {
                "name": "Sea Bass with Lemon Couscous",
                "description": "Grilled sea bass, lemon couscous, herbs, and olive oil.",
                "price": 34,
                "allergens": ["fish", "gluten"],
                "tags": ["popular"],
            },
            {
                "name": "Vegetarian Pasta",
                "description": "Fresh pasta with tomatoes, basil, grilled vegetables, and parmesan.",
                "price": 24,
                "allergens": ["gluten", "milk"],
                "tags": ["vegetarian", "popular"],
            },
            {
                "name": "Harissa Honey Chicken",
                "description": "Roasted chicken, harissa honey glaze, potatoes, and herbs.",
                "price": 29,
                "allergens": [],
                "tags": ["popular"],
            },
            {
                "name": "Grilled Vegetable Plate",
                "description": "Charred seasonal vegetables, chickpeas, herbs, and tahini.",
                "price": 21,
                "allergens": ["sesame"],
                "tags": ["vegan", "vegetarian"],
            },
        ],
    },
    {
        "category": "Desserts",
        "items": [
            {
                "name": "Orange Blossom Creme",
                "description": "Silky custard with orange blossom and pistachio.",
                "price": 10,
                "allergens": ["milk", "egg", "tree nuts"],
                "tags": ["vegetarian"],
            },
            {
                "name": "Date Cake",
                "description": "Warm date cake with cinnamon syrup.",
                "price": 11,
                "allergens": ["gluten", "egg"],
                "tags": ["vegetarian"],
            },
        ],
    },
    {
        "category": "Drinks",
        "items": [
            {
                "name": "Mint Tea",
                "description": "Traditional green tea with fresh mint.",
                "price": 5,
                "allergens": [],
                "tags": ["vegan"],
            },
            {
                "name": "Fresh Lemonade",
                "description": "Lemon, mint, and light cane syrup.",
                "price": 7,
                "allergens": [],
                "tags": ["vegan"],
            },
        ],
    },
]


def restaurant_context() -> str:
    menu_lines = []
    for category in MENU:
        menu_lines.append(f"{category['category']}:")
        for item in category["items"]:
            allergens = ", ".join(item["allergens"]) if item["allergens"] else "none listed"
            tags = ", ".join(item["tags"]) if item["tags"] else "none"
            menu_lines.append(
                f"- {item['name']} ({item['price']} TND): {item['description']} "
                f"Allergens: {allergens}. Tags: {tags}."
            )

    hours = ", ".join(
        f"{day}: {hours}" for day, hours in RESTAURANT["opening_hours"].items()
    )
    faqs = " ".join(f"Q: {faq['question']} A: {faq['answer']}" for faq in RESTAURANT["faqs"])
    delivery = RESTAURANT["delivery"]

    return f"""
Restaurant name: {RESTAURANT['name']}
Address: {RESTAURANT['address']}
Phone: {RESTAURANT['phone']}
Opening hours: {hours}
Popular dishes: {', '.join(RESTAURANT['popular_dishes'])}
Delivery: available={delivery['available']}; hours={delivery['hours']}; areas={', '.join(delivery['areas'])}; minimum order={delivery['minimum_order']} TND; fee={delivery['fee']} TND.
Menu:
{chr(10).join(menu_lines)}
FAQs:
{faqs}
""".strip()
