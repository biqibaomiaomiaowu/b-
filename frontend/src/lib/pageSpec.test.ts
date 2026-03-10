import { describe, it, expect } from 'vitest'
import { parsePageSpecIndexes } from './pageSpec'

describe('parsePageSpecIndexes', () => {
  it('returns empty set for empty spec', () => {
    expect(parsePageSpecIndexes('', 10)).toEqual(new Set())
    expect(parsePageSpecIndexes('   ', 10)).toEqual(new Set())
  })

  it('returns empty set if totalCount is <= 0', () => {
    expect(parsePageSpecIndexes('1-5', 0)).toEqual(new Set())
    expect(parsePageSpecIndexes('1-5', -5)).toEqual(new Set())
  })

  it('handles "ALL" spec', () => {
    expect(parsePageSpecIndexes('ALL', 5)).toEqual(new Set([1, 2, 3, 4, 5]))
    expect(parsePageSpecIndexes('all', 5)).toEqual(new Set([1, 2, 3, 4, 5]))
    expect(parsePageSpecIndexes('  AlL  ', 3)).toEqual(new Set([1, 2, 3]))
  })

  it('handles "LAST" spec', () => {
    expect(parsePageSpecIndexes('LAST', 10)).toEqual(new Set([10]))
    expect(parsePageSpecIndexes('last', 10)).toEqual(new Set([10]))
    expect(parsePageSpecIndexes('  lAsT  ', 5)).toEqual(new Set([5]))
  })

  it('parses single indexes', () => {
    expect(parsePageSpecIndexes('1', 10)).toEqual(new Set([1]))
    expect(parsePageSpecIndexes('3', 10)).toEqual(new Set([3]))
    expect(parsePageSpecIndexes('1, 3, 5', 10)).toEqual(new Set([1, 3, 5]))
  })

  it('ignores single indexes out of bounds', () => {
    expect(parsePageSpecIndexes('0, 11', 10)).toEqual(new Set())
    expect(parsePageSpecIndexes('1, 15', 10)).toEqual(new Set([1]))
  })

  it('parses ranges', () => {
    expect(parsePageSpecIndexes('1-3', 10)).toEqual(new Set([1, 2, 3]))
    expect(parsePageSpecIndexes('2-5', 10)).toEqual(new Set([2, 3, 4, 5]))
  })

  it('parses reversed ranges automatically', () => {
    expect(parsePageSpecIndexes('3-1', 10)).toEqual(new Set([1, 2, 3]))
    expect(parsePageSpecIndexes('5-2', 10)).toEqual(new Set([2, 3, 4, 5]))
  })

  it('ignores out of bound values in ranges', () => {
    expect(parsePageSpecIndexes('0-2', 10)).toEqual(new Set([1, 2]))
    expect(parsePageSpecIndexes('9-12', 10)).toEqual(new Set([9, 10]))
    expect(parsePageSpecIndexes('15-20', 10)).toEqual(new Set())
  })

  it('handles combination of single indexes, ranges, and LAST', () => {
    expect(parsePageSpecIndexes('1, 3-5, LAST', 10)).toEqual(new Set([1, 3, 4, 5, 10]))
    expect(parsePageSpecIndexes('1,3-5,LAST', 10)).toEqual(new Set([1, 3, 4, 5, 10]))
  })

  it('handles invalid segments gracefully', () => {
    expect(parsePageSpecIndexes('abc, 1, def, 3', 10)).toEqual(new Set([1, 3]))
    expect(parsePageSpecIndexes('1-abc, 2', 10)).toEqual(new Set([2]))
  })

  it('deduplicates indexes', () => {
    expect(parsePageSpecIndexes('1, 1, 1-3, 2-4', 10)).toEqual(new Set([1, 2, 3, 4]))
  })
})
