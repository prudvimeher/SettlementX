const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export async function createTrade(tradeData) {
  const response = await fetch(`${API_BASE_URL}/trades`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(tradeData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail?.message ||
        data?.detail ||
        "Failed to create trade"
    );
  }

  return data;
}

export async function validateTrade(tradeId) {
  const response = await fetch(
    `${API_BASE_URL}/trades/${tradeId}/validate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail?.message ||
        data?.detail ||
        "Failed to validate trade"
    );
  }

  return data;
}

export async function confirmTrade(tradeId) {
  const response = await fetch(
    `${API_BASE_URL}/trades/${tradeId}/confirm`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail?.message ||
        data?.detail ||
        "Failed to confirm trade"
    );
  }

  return data;
}