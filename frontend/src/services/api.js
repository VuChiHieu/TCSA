import axios from 'axios'

const BASE_URL = 'http://127.0.0.1:8000'

export const predictFull = async (text, model = 'nb') => {
  const res = await axios.post(`${BASE_URL}/predict/full`, { text, model })
  return res.data
}

export const predictBatch = async (texts, model = 'nb') => {
  const res = await axios.post(`${BASE_URL}/predict/batch`, { texts, model })
  return res.data
}

export const predictToxic = async (text, model = 'nb') => {
  const res = await axios.post(`${BASE_URL}/predict/toxic`, { text, model })
  return res.data
}

export const extractKeywords = async (texts, topN = 5) => {
  const res = await axios.post(`${BASE_URL}/analyze/keywords`, { texts, top_n: topN })
  return res.data
}