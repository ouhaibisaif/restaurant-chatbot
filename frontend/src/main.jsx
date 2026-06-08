import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Bot, CalendarDays, ChefHat, Clock, MessageCircle, Phone, Send, Users } from 'lucide-react';
import './styles.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [activeView, setActiveView] = useState('chat');
  const [menuData, setMenuData] = useState(null);
  const [reservations, setReservations] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/menu`)
      .then((res) => res.json())
      .then(setMenuData)
      .catch(() => setMenuData(null));
  }, []);

  const refreshReservations = () => {
    fetch(`${API_URL}/admin/reservations`)
      .then((res) => res.json())
      .then(setReservations)
      .catch(() => setReservations([]));
  };

  useEffect(() => {
    if (activeView === 'admin') refreshReservations();
  }, [activeView]);

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <p className="eyebrow">Local Qwen assistant</p>
          <h1>{menuData?.restaurant?.name || 'Le Jardin Bleu'}</h1>
        </div>
        <nav className="tabs" aria-label="Main navigation">
          <button className={activeView === 'chat' ? 'active' : ''} onClick={() => setActiveView('chat')}>
            <MessageCircle size={18} /> Chat
          </button>
          <button className={activeView === 'menu' ? 'active' : ''} onClick={() => setActiveView('menu')}>
            <ChefHat size={18} /> Menu
          </button>
          <button className={activeView === 'reserve' ? 'active' : ''} onClick={() => setActiveView('reserve')}>
            <CalendarDays size={18} /> Reserve
          </button>
          <button className={activeView === 'admin' ? 'active' : ''} onClick={() => setActiveView('admin')}>
            <Users size={18} /> Admin
          </button>
        </nav>
      </header>

      <main className="content">
        <RestaurantSummary data={menuData} />
        {activeView === 'chat' && <ChatPanel />}
        {activeView === 'menu' && <MenuPage data={menuData} />}
        {activeView === 'reserve' && <ReservationForm onSaved={() => setActiveView('admin')} />}
        {activeView === 'admin' && <AdminPage reservations={reservations} onRefresh={refreshReservations} />}
      </main>
    </div>
  );
}

function RestaurantSummary({ data }) {
  const restaurant = data?.restaurant;
  if (!restaurant) return null;

  return (
    <section className="summary">
      <div>
        <span><Clock size={16} /> Mon-Sat 11:00-23:00</span>
        <span><Phone size={16} /> {restaurant.phone}</span>
      </div>
      <p>{restaurant.address}</p>
    </section>
  );
}

function ChatPanel() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello. I can help with our menu, opening hours, allergens, delivery, or table reservations.',
    },
  ]);
  const [input, setInput] = useState('');
  const [language, setLanguage] = useState('auto');
  const [sessionId, setSessionId] = useState(localStorage.getItem('restaurant-session-id') || '');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async (event) => {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const nextMessages = [...messages, { role: 'user', content: trimmed }];
    setMessages(nextMessages);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: trimmed,
          language,
          session_id: sessionId || null,
          history: nextMessages.slice(-8),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Chat failed');
      setSessionId(data.session_id);
      localStorage.setItem('restaurant-session-id', data.session_id);
      setMessages((current) => [...current, { role: 'assistant', content: data.reply }]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        { role: 'assistant', content: `Sorry, I could not answer right now. ${error.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel chat-panel">
      <div className="panel-header">
        <div>
          <h2>Restaurant Chat</h2>
          <p>Grounded in local restaurant data and powered by Qwen through Ollama.</p>
        </div>
        <select value={language} onChange={(event) => setLanguage(event.target.value)} aria-label="Language">
          <option value="auto">Auto</option>
          <option value="en">English</option>
          <option value="fr">Francais</option>
          <option value="ar">Arabic</option>
        </select>
      </div>

      <div className="messages">
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={`message ${message.role}`}>
            {message.role === 'assistant' && <Bot size={18} />}
            <p dir={isArabic(message.content) ? 'rtl' : 'ltr'}>{message.content}</p>
          </div>
        ))}
        {loading && <div className="message assistant"><Bot size={18} /><p>Thinking...</p></div>}
        <div ref={bottomRef} />
      </div>

      <form className="chat-input" onSubmit={sendMessage}>
        <input
          value={input}
          maxLength={1000}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about hours, dishes, allergens, delivery, or reservations..."
        />
        <button type="submit" disabled={loading || !input.trim()} aria-label="Send message">
          <Send size={18} />
        </button>
      </form>
    </section>
  );
}

function MenuPage({ data }) {
  if (!data) return <section className="panel"><h2>Menu unavailable</h2></section>;
  const popular = new Set(data.restaurant.popular_dishes);

  return (
    <section className="menu-view">
      {data.menu.map((category) => (
        <div className="panel" key={category.category}>
          <h2>{category.category}</h2>
          <div className="menu-grid">
            {category.items.map((item) => (
              <article className="dish-card" key={item.name}>
                <div>
                  <h3>{item.name}</h3>
                  {popular.has(item.name) && <span className="badge">Popular</span>}
                </div>
                <p>{item.description}</p>
                <small>Allergens: {item.allergens.length ? item.allergens.join(', ') : 'none listed'}</small>
                <strong>{item.price} TND</strong>
              </article>
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}

function ReservationForm({ onSaved }) {
  const [form, setForm] = useState({
    name: '',
    phone: '',
    reservation_date: '',
    reservation_time: '',
    people: 2,
    notes: '',
  });
  const [status, setStatus] = useState('');

  const isValid = useMemo(() => {
    return form.name.trim().length >= 2 && form.phone.trim().length >= 6 && form.reservation_date && form.reservation_time && Number(form.people) > 0;
  }, [form]);

  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  const submit = async (event) => {
    event.preventDefault();
    if (!isValid) return;
    setStatus('Saving reservation...');
    try {
      const response = await fetch(`${API_URL}/reservation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, people: Number(form.people), source: 'form' }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Reservation failed');
      setStatus(`Reservation request #${data.id} saved.`);
      onSaved?.();
    } catch (error) {
      setStatus(error.message);
    }
  };

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Reservation Request</h2>
          <p>Requests are saved locally in SQLite as pending reservations.</p>
        </div>
      </div>
      <form className="reservation-form" onSubmit={submit}>
        <label>Name<input value={form.name} onChange={(e) => update('name', e.target.value)} required minLength={2} /></label>
        <label>Phone<input value={form.phone} onChange={(e) => update('phone', e.target.value)} required minLength={6} /></label>
        <label>Date<input type="date" value={form.reservation_date} onChange={(e) => update('reservation_date', e.target.value)} required /></label>
        <label>Time<input type="time" value={form.reservation_time} onChange={(e) => update('reservation_time', e.target.value)} required /></label>
        <label>People<input type="number" min="1" max="30" value={form.people} onChange={(e) => update('people', e.target.value)} required /></label>
        <label className="wide">Notes<textarea value={form.notes} maxLength={500} onChange={(e) => update('notes', e.target.value)} /></label>
        <button type="submit" disabled={!isValid}>Save request</button>
      </form>
      {status && <p className="status">{status}</p>}
    </section>
  );
}

function AdminPage({ reservations, onRefresh }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Reservations</h2>
          <p>Local admin view for pending customer requests.</p>
        </div>
        <button className="secondary" onClick={onRefresh}>Refresh</button>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Phone</th>
              <th>Date</th>
              <th>Time</th>
              <th>People</th>
              <th>Source</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {reservations.map((reservation) => (
              <tr key={reservation.id}>
                <td>{reservation.id}</td>
                <td>{reservation.name}</td>
                <td>{reservation.phone}</td>
                <td>{reservation.reservation_date}</td>
                <td>{reservation.reservation_time}</td>
                <td>{reservation.people}</td>
                <td>{reservation.source}</td>
                <td>{reservation.status}</td>
              </tr>
            ))}
            {!reservations.length && (
              <tr><td colSpan="8">No reservations yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function isArabic(text) {
  return /[\u0600-\u06FF]/.test(text);
}

createRoot(document.getElementById('root')).render(<App />);
