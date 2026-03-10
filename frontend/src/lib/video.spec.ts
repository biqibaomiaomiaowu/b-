import { describe, it, expect } from 'vitest'
import { extractBilibiliTarget } from './video'

describe('extractBilibiliTarget', () => {
  it('returns empty string for empty input', () => {
    expect(extractBilibiliTarget('')).toBe('')
    expect(extractBilibiliTarget('   ')).toBe('')
  })

  it('extracts URL properly', () => {
    expect(extractBilibiliTarget('https://www.bilibili.com/video/BV1xx411c7mD')).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
    expect(extractBilibiliTarget('http://b23.tv/abcd')).toBe('http://b23.tv/abcd')
    // extracts URL inside text
    expect(extractBilibiliTarget('Check this out: https://www.bilibili.com/video/BV1xx411c7mD !')).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
  })

  it('removes trailing punctuation from extracted URL', () => {
    expect(extractBilibiliTarget('https://www.bilibili.com/video/BV1xx411c7mD,')).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
    expect(extractBilibiliTarget('https://www.bilibili.com/video/BV1xx411c7mD;')).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
    expect(extractBilibiliTarget('https://www.bilibili.com/video/BV1xx411c7mD.')).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
    expect(extractBilibiliTarget('https://www.bilibili.com/video/BV1xx411c7mD!')).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
    expect(extractBilibiliTarget('https://www.bilibili.com/video/BV1xx411c7mD?')).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
    expect(extractBilibiliTarget('https://www.bilibili.com/video/BV1xx411c7mD]')).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
    expect(extractBilibiliTarget('https://www.bilibili.com/video/BV1xx411c7mD)')).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
    expect(extractBilibiliTarget('https://www.bilibili.com/video/BV1xx411c7mD>')).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
    expect(extractBilibiliTarget('https://www.bilibili.com/video/BV1xx411c7mD}}')).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
  })

  it('extracts Bilibili IDs and formats prefix casing', () => {
    // BV
    expect(extractBilibiliTarget('BV1xx411c7mD')).toBe('BV1xx411c7mD')
    expect(extractBilibiliTarget('bv1xx411c7md')).toBe('BV1xx411c7md') // It preserves casing of the rest
    expect(extractBilibiliTarget('Bv1xx411c7mD')).toBe('BV1xx411c7mD')
    expect(extractBilibiliTarget('bV1xx411c7mD')).toBe('BV1xx411c7mD')

    // av
    expect(extractBilibiliTarget('av12345678')).toBe('av12345678')
    expect(extractBilibiliTarget('AV12345678')).toBe('av12345678')
    expect(extractBilibiliTarget('Av12345678')).toBe('av12345678')
    expect(extractBilibiliTarget('aV12345678')).toBe('av12345678')

    // ep
    expect(extractBilibiliTarget('ep1234')).toBe('ep1234')
    expect(extractBilibiliTarget('EP1234')).toBe('ep1234')
    expect(extractBilibiliTarget('Ep1234')).toBe('ep1234')

    // ss
    expect(extractBilibiliTarget('ss1234')).toBe('ss1234')
    expect(extractBilibiliTarget('SS1234')).toBe('ss1234')
  })

  it('extracts IDs embedded within text', () => {
    expect(extractBilibiliTarget('Here is the video: BV1xx411c7mD.')).toBe('BV1xx411c7mD')
    expect(extractBilibiliTarget('av12345678 is great')).toBe('av12345678')
    expect(extractBilibiliTarget('Watch ep1234 today')).toBe('ep1234')
  })

  it('returns original trimmed text if no URL or ID is found', () => {
    expect(extractBilibiliTarget('Just some random text')).toBe('Just some random text')
    expect(extractBilibiliTarget('   Text with spaces   ')).toBe('Text with spaces')
    // Partial matches shouldn't be extracted as IDs (e.g. less than 10 chars for BV)
    expect(extractBilibiliTarget('BV123')).toBe('BV123')
  })
})
