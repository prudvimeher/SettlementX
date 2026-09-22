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

export async function createSettlement(tradeId) {
  const response = await fetch(
    `${API_BASE_URL}/trades/${tradeId}/settlement`,
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
        "Failed to create settlement"
    );
  }

  return data;
}

export async function simulateCashTransfer({
  settlementId,
  amount,
  currency,
  scenario,
}) {
  const response = await fetch(
    `${API_BASE_URL}/external/cash-transfer`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        settlement_id: settlementId,
        amount: String(amount),
        currency,
        scenario,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail?.message ||
        data?.detail ||
        "Cash transfer failed"
    );
  }

  return data;
}


export async function simulateAssetTransfer({
  settlementId,
  quantity,
  instrument,
  scenario,
}) {
  const response = await fetch(
    `${API_BASE_URL}/external/asset-transfer`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        settlement_id: settlementId,
        quantity: String(quantity),
        instrument,
        scenario,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail?.message ||
        data?.detail ||
        "Asset transfer failed"
    );
  }

  return data;
}