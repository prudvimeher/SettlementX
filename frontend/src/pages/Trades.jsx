import { useEffect, useState } from "react";
import TradeForm from "../components/TradeForm";
import {
  validateTrade,
  confirmTrade,
  createSettlement,
  simulateCashTransfer,
  simulateAssetTransfer,
} from "../services/tradeService";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

function Trades() {
  const [trades, setTrades] = useState([]);
  const [settlements, setSettlements] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [scenario, setScenario] = useState("success");
  const [externalResults, setExternalResults] = useState({});


  const fetchTrades = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/trades`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error("Failed to load trades");
      }

      setTrades(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrades();
  }, []);

  const handleValidate = async (tradeId) => {
    try {
      setError("");
      await validateTrade(tradeId);
      await fetchTrades();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleConfirm = async (tradeId) => {
    try {
      setError("");
      await confirmTrade(tradeId);
      await fetchTrades();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCreateSettlement = async (tradeId) => {
    try {
      setError("");

      const data = await createSettlement(tradeId);

      setSettlements((current) => ({
        ...current,
        [tradeId]: data,
      }));
    } catch (err) {
      setError(err.message);
    }
  };
  const handleCashTransfer = async (settlement) => {
  try {
    setError("");

    const result = await simulateCashTransfer({
      settlementId: settlement.settlement_id,
      amount: settlement.cash_amount,
      currency: settlement.currency,
      scenario,
    });

    setExternalResults((current) => ({
      ...current,
      [`${settlement.settlement_id}-cash`]: result,
    }));
  } catch (err) {
    setError(err.message);
  }
};

const handleAssetTransfer = async (settlement) => {
  try {
    setError("");

    const result = await simulateAssetTransfer({
      settlementId: settlement.settlement_id,
      quantity: settlement.asset_quantity,
      instrument: settlement.instrument,
      scenario,
    });

    setExternalResults((current) => ({
      ...current,
      [`${settlement.settlement_id}-asset`]: result,
    }));
  } catch (err) {
    setError(err.message);
  }
};

  return (
  <div className="bnpp-page">
    <div className="bnpp-header">
      <div>
        <div className="bnpp-eyebrow">SETTLEMENTX</div>
        <h1>Trade Operations</h1>
        <p>Trade capture, confirmation and settlement instruction</p>
      </div>
    </div>

    <TradeForm />

    {error && (
      <div className="bnpp-error">
        {error}
      </div>
    )}

    {loading ? (
      <div className="bnpp-panel">Loading trades...</div>
    ) : (
      <div className="bnpp-panel">
        <div className="bnpp-panel-header">
          <h2>Trade Book</h2>
          <span>{trades.length} trades</span>
        </div>

        <div className="bnpp-table-wrapper">
          <table className="bnpp-table">
            <thead>
              <tr>
                <th>Trade ID</th>
                <th>Buyer</th>
                <th>Seller</th>
                <th>Instrument</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Value</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {trades.map((trade) => {
                const settlement = settlements[trade.trade_id];

                return (
                  <tr key={trade.trade_id}>
                    <td className="bnpp-mono">
                      {trade.trade_id}
                    </td>

                    <td>{trade.buyer}</td>
                    <td>{trade.seller}</td>
                    <td>{trade.instrument}</td>
                    <td>{trade.quantity}</td>

                    <td>
                      {trade.currency} {trade.price}
                    </td>

                    <td>
                      {trade.currency}{" "}
                      {(
                        Number(trade.quantity) *
                        Number(trade.price)
                      ).toLocaleString("en-IN")}
                    </td>

                    <td>
                      <span
                        className={`bnpp-status status-${trade.status.toLowerCase()}`}
                      >
                        {trade.status}
                      </span>
                    </td>

                    <td>
                      {trade.status === "CAPTURED" && (
                        <button
                          className="bnpp-button"
                          onClick={() =>
                            handleValidate(trade.trade_id)
                          }
                        >
                          Validate
                        </button>
                      )}

                      {trade.status === "VALIDATED" && (
                        <button
                          className="bnpp-button"
                          onClick={() =>
                            handleConfirm(trade.trade_id)
                          }
                        >
                          Confirm Trade
                        </button>
                      )}

                      {trade.status === "CONFIRMED" &&
                        !settlement && (
                          <button
                            className="bnpp-button bnpp-button-primary"
                            onClick={() =>
                              handleCreateSettlement(
                                trade.trade_id
                              )
                            }
                          >
                            Create Settlement
                          </button>
                        )}

                      {trade.status === "CONFIRMED" &&
                        settlement && (
                          <span className="bnpp-complete">
                            Settlement Created
                          </span>
                        )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    )}

    {Object.values(settlements).map((settlement) => (
      <div
        className="bnpp-panel settlement-panel"
        key={settlement.settlement_id}
      >
        <div className="bnpp-panel-header">
          <div>
            <div className="bnpp-eyebrow">
              SETTLEMENT INSTRUCTION
            </div>

            <h2>{settlement.settlement_id}</h2>
          </div>

          <span className="bnpp-status status-instructed">
            {settlement.status}
          </span>
        </div>

        {/* PHASE 7 — EXTERNAL SYSTEM SIMULATOR */}

        <div className="simulator-toolbar">
          <div>
            <div className="bnpp-eyebrow">
              EXTERNAL SYSTEM SIMULATOR
            </div>

            <div className="simulator-title">
              Test external settlement outcome
            </div>
          </div>

          <select
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
            className="scenario-select"
          >
            <option value="success">SUCCESS</option>
            <option value="failure">FAILURE</option>
            <option value="timeout">TIMEOUT</option>
            <option value="duplicate">DUPLICATE</option>
          </select>
        </div>

        <div className="settlement-grid">

          {/* CASH LEG */}

          <div className="settlement-leg">
            <div className="leg-label">
              CASH
            </div>

            <div className="leg-value">
              {settlement.currency}{" "}
              {Number(
                settlement.cash_amount
              ).toLocaleString("en-IN")}
            </div>

            <div className="leg-route">
              Buyer → Seller
            </div>

            <span className="bnpp-status status-pending">
              {settlement.cash_status}
            </span>

            <div className="leg-action">
              <button
                className="bnpp-button"
                onClick={() =>
                  handleCashTransfer(settlement)
                }
              >
                Send Cash
              </button>
            </div>

            {externalResults[
              `${settlement.settlement_id}-cash`
            ] && (
              <div className="external-result">
                <strong>
                  {
                    externalResults[
                      `${settlement.settlement_id}-cash`
                    ].status
                  }
                </strong>

                <span>
                  {
                    externalResults[
                      `${settlement.settlement_id}-cash`
                    ].message
                  }
                </span>
              </div>
            )}
          </div>

          {/* ASSET LEG */}

          <div className="settlement-leg">
            <div className="leg-label">
              ASSET
            </div>

            <div className="leg-value">
              {settlement.asset_quantity}{" "}
              {settlement.instrument}
            </div>

            <div className="leg-route">
              Seller → Buyer
            </div>

            <span className="bnpp-status status-pending">
              {settlement.asset_status}
            </span>

            <div className="leg-action">
              <button
                className="bnpp-button"
                onClick={() =>
                  handleAssetTransfer(settlement)
                }
              >
                Send Asset
              </button>
            </div>

            {externalResults[
              `${settlement.settlement_id}-asset`
            ] && (
              <div className="external-result">
                <strong>
                  {
                    externalResults[
                      `${settlement.settlement_id}-asset`
                    ].status
                  }
                </strong>

                <span>
                  {
                    externalResults[
                      `${settlement.settlement_id}-asset`
                    ].message
                  }
                </span>
              </div>
            )}
          </div>

        </div>
      </div>
    ))}
  </div>
);
}

export default Trades;