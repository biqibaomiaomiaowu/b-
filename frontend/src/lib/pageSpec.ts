export function normalizePageSpec(value: string): string {
  const trimmed = value.trim()
  if (!trimmed) {
    return ''
  }

  const upperValue = trimmed.toUpperCase()
  if (upperValue === 'ALL' || upperValue === 'LAST') {
    return upperValue
  }

  return trimmed.replace(/\s+/g, '')
}

export function parsePageSpecIndexes(spec: string, totalCount: number): Set<number> {
  const result = new Set<number>()
  const raw = normalizePageSpec(spec)
  if (!raw || totalCount <= 0) {
    return result
  }

  if (raw === 'ALL') {
    for (let index = 1; index <= totalCount; index += 1) {
      result.add(index)
    }
    return result
  }

  for (const segment of raw.split(',').map((item) => item.trim()).filter(Boolean)) {
    if (segment === 'LAST') {
      result.add(totalCount)
      continue
    }

    const rangeMatch = segment.match(/^(\d+)-(\d+)$/)
    if (rangeMatch) {
      let start = Number(rangeMatch[1])
      let end = Number(rangeMatch[2])
      if (Number.isNaN(start) || Number.isNaN(end)) {
        continue
      }
      if (start > end) {
        ;[start, end] = [end, start]
      }
      for (let index = start; index <= end; index += 1) {
        if (index >= 1 && index <= totalCount) {
          result.add(index)
        }
      }
      continue
    }

    const index = Number(segment)
    if (!Number.isNaN(index) && index >= 1 && index <= totalCount) {
      result.add(index)
    }
  }

  return result
}

export function buildPageSpecFromIndexes(indexes: Iterable<number>, totalCount: number): string {
  const sorted = Array.from(indexes)
    .filter((value) => value >= 1 && value <= totalCount)
    .sort((left, right) => left - right)

  if (!sorted.length) {
    return ''
  }
  if (sorted.length === totalCount) {
    return 'ALL'
  }
  if (sorted.length === 1 && sorted[0] === totalCount) {
    return 'LAST'
  }

  const segments: string[] = []
  let start = sorted[0]
  let previous = sorted[0]

  for (let index = 1; index <= sorted.length; index += 1) {
    const value = sorted[index]
    if (value === previous + 1) {
      previous = value
      continue
    }
    segments.push(start === previous ? String(start) : `${start}-${previous}`)
    start = value
    previous = value
  }

  return segments.join(',')
}
