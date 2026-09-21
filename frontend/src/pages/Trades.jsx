import { useEffect, useState } from "react";
import TradeForm from "../components/TradeForm";
import {
  validateTrade,
  confirmTrade,
} from "../services/tradeService";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

function Trades() {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchTrades = async () => {
    try {
      setError("");

      const response = await fetch(`${API_BASE_URL}/trades`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail?.message ||
            data?.detail ||
            "Failed to load trades"
        );
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

  return (
    <div>
      <TradeForm onTradeCreated={fetchTrades} />

      {error && (
        <div className="mx-auto w-full max-w-6xl px-4 pb-4">
          <div className="border border-[#d64545] bg-[#fff1f1] px-4 py-3 text-sm text-[#d64545]">
            {error}
          </div>
        </div>
      )}

      <div className="mx-auto w-full max-w-6xl px-4 pb-8">
        <div className="border border-[#dce5e0] bg-white">
          <div className="border-b border-[#dce5e0] bg-[#f4f7f5] px-6 py-4">
            <h2 className="text-sm font-semibold text-[#17221d]">
              Trades
            </h2>
          </div>

          {loading ? (
            <div className="p-6 text-sm text-[#5f6b66]">
              Loading trades...
            </div>
          ) : trades.length === 0 ? (
            <div className="p-6 text-sm text-[#5f6b66]">
              No trades found.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-[#dce5e0] bg-[#f4f7f5]">
                  <tr>
                    <th className="px-4 py-3">Trade ID</th>
                    <th className="px-4 py-3">Buyer</th>
                    <th className="px-4 py-3">Seller</th>
                    <th className="px-4 py-3">Instrument</th>
                    <th className="px-4 py-3">Quantity</th>
                    <th className="px-4 py-3">Price</th>
                    <th className="px-4 py-3">Currency</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Action</th>
                  </tr>
                </thead>

                <tbody>
                  {trades.map((trade) => (
                    <tr
                      key={trade.trade_id}
                      className="border-b border-[#dce5e0]"
                    >
                      <td className="px-4 py-3 font-medium">
                        {trade.trade_id}
                      </td>

                      <td className="px-4 py-3">
                        {trade.buyer}
                      </td>

                      <td className="px-4 py-3">
                        {trade.seller}
                      </td>

                      <td className="px-4 py-3">
                        {trade.instrument}
                      </td>

                      <td className="px-4 py-3">
                        {trade.quantity}
                      </td>

                      <td className="px-4 py-3">
                        {trade.price}
                      </td>

                      <td className="px-4 py-3">
                        {trade.currency}
                      </td>

                      <td className="px-4 py-3 font-semibold">
                        {trade.status}
                      </td>

                      <td className="px-4 py-3">
                        {trade.status === "CAPTURED" && (
                          <button
                            type="button"
                            onClick={() =>
                              handleValidate(trade.trade_id)
                            }
                            className="bg-[#00915a] px-4 py-2 text-xs font-semibold text-white hover:bg-[#17221d]"
                          >
                            Validate
                          </button>
                        )}

                        {trade.status === "VALIDATED" && (
                          <button
                            onClick={() => handleConfirm(trade.trade_id)}
                            className="font-semibold text-[#00915a]"
                          >
                            Confirm Trade
                          </button>
                        )}

                        {trade.status === "CONFIRMED" && (
                          <span className="font-semibold text-[#00915a]">
                          Confirmed
                          </span>
                        )}

                        {trade.status === "REJECTED" && (
                          <span className="font-semibold text-[#d64545]">
                            Rejected
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Trades;