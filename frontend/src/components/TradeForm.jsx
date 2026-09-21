import { useState } from "react";
import { createTrade } from "../services/tradeService";

function TradeForm({ onTradeCreated }) {
  const [formData, setFormData] = useState({
    trade_id: "",
    buyer: "",
    seller: "",
    instrument: "",
    quantity: "",
    price: "",
    currency: "INR",
    trade_date: "",
    settlement_date: "",
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setLoading(true);
    setMessage("");
    setError("");

    try {
      const data = await createTrade({
        ...formData,
        quantity: Number(formData.quantity),
        price: Number(formData.price),
      });

      setMessage(`Trade created successfully — Status: ${data.status}`);
      onTradeCreated();
      setFormData({
        trade_id: "",
        buyer: "",
        seller: "",
        instrument: "",
        quantity: "",
        price: "",
        currency: "INR",
        trade_date: "",
        settlement_date: "",
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    "w-full border border-[#dce5e0] bg-white px-3 py-2.5 text-sm text-[#17221d] outline-none focus:border-[#00915a] focus:ring-1 focus:ring-[#00915a]";

  const labelClass =
    "mb-1.5 block text-sm font-medium text-[#17221d]";

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-8">
      <div className="mb-6 border-b border-[#dce5e0] pb-4">
        <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#00915a]">
          Trade Management
        </p>

        <h2 className="text-2xl font-semibold text-[#17221d]">
          Create Trade
        </h2>

        <p className="mt-1 text-sm text-[#5f6b66]">
          Capture a new trade for validation and settlement processing.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="border border-[#dce5e0] bg-white"
      >
        <div className="border-b border-[#dce5e0] bg-[#f4f7f5] px-6 py-4">
          <h3 className="text-sm font-semibold text-[#17221d]">
            Trade Details
          </h3>

          <p className="mt-1 text-xs text-[#5f6b66]">
            Enter the required trade information below.
          </p>
        </div>

        <div className="space-y-6 p-6">
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div>
              <label className={labelClass}>Trade ID</label>

              <input
                name="trade_id"
                placeholder="e.g. T1001"
                value={formData.trade_id}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </div>

            <div>
              <label className={labelClass}>Instrument</label>

              <input
                name="instrument"
                placeholder="e.g. RELIANCE"
                value={formData.instrument}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div>
              <label className={labelClass}>Buyer</label>

              <input
                name="buyer"
                placeholder="Buyer name"
                value={formData.buyer}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </div>

            <div>
              <label className={labelClass}>Seller</label>

              <input
                name="seller"
                placeholder="Seller name"
                value={formData.seller}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
            <div>
              <label className={labelClass}>Quantity</label>

              <input
                name="quantity"
                type="number"
                min="0"
                step="0.0001"
                placeholder="0.0000"
                value={formData.quantity}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </div>

            <div>
              <label className={labelClass}>Price</label>

              <input
                name="price"
                type="number"
                min="0"
                step="0.0001"
                placeholder="0.0000"
                value={formData.price}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </div>

            <div>
              <label className={labelClass}>Currency</label>

              <input
                name="currency"
                placeholder="INR"
                value={formData.currency}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </div>
          </div>

          <div className="border-t border-[#dce5e0] pt-6">
            <h3 className="mb-4 text-sm font-semibold text-[#17221d]">
              Settlement Schedule
            </h3>

            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              <div>
                <label className={labelClass}>Trade Date</label>

                <input
                  name="trade_date"
                  type="date"
                  value={formData.trade_date}
                  onChange={handleChange}
                  className={inputClass}
                  required
                />
              </div>

              <div>
                <label className={labelClass}>Settlement Date</label>

                <input
                  name="settlement_date"
                  type="date"
                  value={formData.settlement_date}
                  onChange={handleChange}
                  className={inputClass}
                  required
                />
              </div>
            </div>
          </div>

          {message && (
            <div className="border border-[#00915a] bg-[#eaf6f0] px-4 py-3 text-sm text-[#006b43]">
              {message}
            </div>
          )}

          {error && (
            <div className="border border-[#d64545] bg-[#fff1f1] px-4 py-3 text-sm text-[#d64545]">
              {error}
            </div>
          )}

          <div className="flex justify-end border-t border-[#dce5e0] pt-5">
            <button
              type="submit"
              disabled={loading}
              className="bg-[#00915a] px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-[#17221d] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Creating..." : "Create Trade"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

export default TradeForm;