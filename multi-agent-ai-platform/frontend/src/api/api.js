import axios from "axios";

const client = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export async function askAgents(query) {
  const response = await client.post("/ask", { query });
  return response.data;
}

