import { describe, it, expect } from 'vitest'
import { buildPageSpecFromIndexes } from './pageSpec'

describe('buildPageSpecFromIndexes', () => {
  it('returns empty string for empty inputs', () => {
    expect(buildPageSpecFromIndexes([], 10)).toBe('')
    expect(buildPageSpecFromIndexes(new Set(), 10)).toBe('')
  })

  it('returns empty string when all inputs are out of bounds', () => {
    expect(buildPageSpecFromIndexes([0, 11, -1], 10)).toBe('')
  })

  it('returns "ALL" when inputs cover all pages', () => {
    expect(buildPageSpecFromIndexes([1, 2, 3, 4, 5], 5)).toBe('ALL')
    expect(buildPageSpecFromIndexes(new Set([1, 2, 3, 4, 5]), 5)).toBe('ALL')
  })

  it('returns "LAST" when the only input is the last page', () => {
    expect(buildPageSpecFromIndexes([10], 10)).toBe('LAST')
    expect(buildPageSpecFromIndexes(new Set([10]), 10)).toBe('LAST')
  })

  it('formats consecutive ranges', () => {
    expect(buildPageSpecFromIndexes([1, 2, 3], 10)).toBe('1-3')
    expect(buildPageSpecFromIndexes([5, 6, 7, 8], 10)).toBe('5-8')
  })

  it('formats individual unconnected numbers', () => {
    expect(buildPageSpecFromIndexes([1, 3, 5], 10)).toBe('1,3,5')
  })

  it('formats mixed ranges and unconnected numbers', () => {
    expect(buildPageSpecFromIndexes([1, 2, 3, 5, 7, 8, 9], 10)).toBe('1-3,5,7-9')
    expect(buildPageSpecFromIndexes([1, 4, 5, 6, 9], 10)).toBe('1,4-6,9')
  })

  it('sorts unordered inputs', () => {
    expect(buildPageSpecFromIndexes([3, 1, 2], 10)).toBe('1-3')
    expect(buildPageSpecFromIndexes([9, 5, 7, 1, 8, 2, 3], 10)).toBe('1-3,5,7-9')
  })

  it('filters out out-of-bounds inputs and duplicates', () => {
    expect(buildPageSpecFromIndexes([-1, 0, 1, 2, 2, 3, 11, 12], 10)).toBe('1-3')
  })
})
