const urlPattern = /https?:\/\/[^\s"'<>]+/i
const bilibiliIdPattern = /\b(BV[0-9A-Za-z]{10}|av\d+|ep\d+|ss\d+)\b/i

export function extractBilibiliTarget(rawText: string): string {
  const text = rawText.trim()
  if (!text) {
    return ''
  }

  const urlMatch = text.match(urlPattern)
  if (urlMatch) {
    return urlMatch[0].replace(/[)\]}>,.;!?]+$/u, '')
  }

  const idMatch = text.match(bilibiliIdPattern)
  if (!idMatch) {
    return text
  }

  const value = idMatch[1]
  const lowerValue = value.toLowerCase()
  if (lowerValue.startsWith('bv')) {
    return `BV${value.slice(2)}`
  }
  if (lowerValue.startsWith('av')) {
    return `av${value.slice(2)}`
  }
  return lowerValue
}
