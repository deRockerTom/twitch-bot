'use client';

import { useEffect, useState } from 'react';

type Message = {
    user_id: string;
    login: string;
    message: string;
    timestamp: string;
}
export default function Overlay() {
  const [visible, setVisible] = useState(false);
  const [data, setData] = useState<Message>();


  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8081/`);
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data) as Message;
      console.log(data);
      setData(data);
      setVisible(true);
      setTimeout(() => setVisible(false), 5000);
    };
    return () => ws.close();
  }, []);

  return (
    <div
      className={`
        fixed bottom-12 left-12 px-6 py-4 text-4xl font-bold text-white
        bg-black bg-opacity-60 rounded-lg shadow-lg transform transition-all
        ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'}
      `}
    >
      {data?.login ?? ''}: {data?.message ?? ''}
    </div>
  );
}
