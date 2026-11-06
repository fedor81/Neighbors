import { BrowserRouter, Routes, Route } from "react-router-dom";

// Каркас маршрутизации: страницы соответствуют use cases спецификации.
const Placeholder = ({ name }: { name: string }) => (
  <div style={{ padding: 24 }}>
    <h1>{name}</h1>
    <p>TODO: реализовать страницу.</p>
  </div>
);

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Placeholder name="Витрина (UC-3): локальная выдача + fallback город" />} />
        <Route path="/login" element={<Placeholder name="Вход по телефону (UC-1)" />} />
        <Route path="/item/:id" element={<Placeholder name="Карточка вещи + запрос аренды" />} />
        <Route path="/new-item" element={<Placeholder name="Добавление вещи (UC-6)" />} />
        <Route path="/bookings" element={<Placeholder name="Мои сделки (UC-4/5): статусы, кнопки цикла" />} />
        <Route path="/chat/:bookingId" element={<Placeholder name="Чат сделки (UC-4, WebSocket)" />} />
        <Route path="/profile" element={<Placeholder name="Профиль, точка, баланс, история (UC-2/7)" />} />
        <Route path="/admin" element={<Placeholder name="Админка модератора (UC-9/10)" />} />
      </Routes>
    </BrowserRouter>
  );
}
