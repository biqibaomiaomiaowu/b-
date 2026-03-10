import { describe, it, expect } from 'vitest'
import { mergeQualityOptions } from './defaults'

describe('mergeQualityOptions', () => {
  it('merges two arrays with unique values', () => {
    const base = ['1080P', '720P']
    const extra = ['4K', '8K']
    expect(mergeQualityOptions(base, extra)).toEqual(['1080P', '720P', '4K', '8K'])
  })

  it('removes duplicate values', () => {
    const base = ['1080P', '720P']
    const extra = ['720P', '480P', '1080P']
    expect(mergeQualityOptions(base, extra)).toEqual(['1080P', '720P', '480P'])
  })

  it('filters out falsy values', () => {
    const base = ['1080P', '', '720P', undefined, null] as string[]
    const extra = ['480P', '']
    expect(mergeQualityOptions(base, extra)).toEqual(['1080P', '720P', '480P'])
  })

  it('maintains the correct order of the first appearance', () => {
    const base = ['A', 'B']
    const extra = ['C', 'A', 'D', 'B']
    expect(mergeQualityOptions(base, extra)).toEqual(['A', 'B', 'C', 'D'])
  })

  it('handles empty arrays', () => {
    expect(mergeQualityOptions([], [])).toEqual([])
    expect(mergeQualityOptions(['1080P'], [])).toEqual(['1080P'])
    expect(mergeQualityOptions([], ['1080P'])).toEqual(['1080P'])
  })
})
