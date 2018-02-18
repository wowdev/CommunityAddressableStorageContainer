import os
import sys
import bin
import salsa20
import secrets
import random

class mode_normal:
  def __call__(self, data):
    return ( b'N'
           + data
           )

# known keys by blizzard
# todo: own keys
salsa20_keys = { bin.BE_hex(b'FA505078126ACB3E'): bin.hex(b'BDC51862ABED79B2DE48C8E7E66C6200')
               , bin.BE_hex(b'402CD9D8D6BFED98'): bin.hex(b'AEB0EADEA47612FE6C041A03958DF241')
               , bin.BE_hex(b'DBD3371554F60306'): bin.hex(b'34E397ACE6DD30EEFDC98A2AB093CD3C')
               , bin.BE_hex(b'FB680CB6A8BF81F3'): bin.hex(b'62D90EFA7F36D71C398AE2F1FE37BDB9')
               , bin.BE_hex(b'11A9203C9881710A'): bin.hex(b'2E2CB8C397C2F24ED0B5E452F18DC267')
               , bin.BE_hex(b'A19C4F859F6EFA54'): bin.hex(b'0196CB6F5ECBAD7CB5283891B9712B4B')
               , bin.BE_hex(b'87AEBBC9C4E6B601'): bin.hex(b'685E86C6063DFDA6C9E85298076B3D42')
               , bin.BE_hex(b'DEE3A0521EFF6F03'): bin.hex(b'AD740CE3FFFF9231468126985708E1B9')
               , bin.BE_hex(b'8C9106108AA84F07'): bin.hex(b'53D859DDA2635A38DC32E72B11B32F29')
               , bin.BE_hex(b'49166D358A34D815'): bin.hex(b'667868CD94EA0135B9B16C93B1124ABA')
               , bin.BE_hex(b'1463A87356778D14'): bin.hex(b'69BD2A78D05C503E93994959B30E5AEC')
               , bin.BE_hex(b'5E152DE44DFBEE01'): bin.hex(b'E45A1793B37EE31A8EB85CEE0EEE1B68')
               , bin.BE_hex(b'9B1F39EE592CA415'): bin.hex(b'54A99F081CAD0D08F7E336F4368E894C')
               , bin.BE_hex(b'24C8B75890AD5917'): bin.hex(b'31100C00FDE0CE18BBB33F3AC15B309F')
               , bin.BE_hex(b'EA658B75FDD4890F'): bin.hex(b'DEC7A4E721F425D133039895C36036F8')
               , bin.BE_hex(b'026FDCDF8C5C7105'): bin.hex(b'8F41809DA55366AD416D3C337459EEE3')
               , bin.BE_hex(b'CAE3FAC925F20402'): bin.hex(b'98B78E8774BF275093CB1B5FC714511B')
               , bin.BE_hex(b'061581CA8496C80C'): bin.hex(b'DA2EF5052DB917380B8AA6EF7A5F8E6A')
               , bin.BE_hex(b'BE2CB0FAD3698123'): bin.hex(b'902A1285836CE6DA5895020DD603B065')
               , bin.BE_hex(b'57A5A33B226B8E0A'): bin.hex(b'FDFC35C99B9DB11A326260CA246ACB41')
               , bin.BE_hex(b'42B9AB1AF5015920'): bin.hex(b'C68778823C964C6F247ACC0F4A2584F8')
               , bin.BE_hex(b'4F0FE18E9FA1AC1A'): bin.hex(b'89381C748F6531BBFCD97753D06CC3CD')
               , bin.BE_hex(b'7758B2CF1E4E3E1B'): bin.hex(b'3DE60D37C664723595F27C5CDBF08BFA')
               , bin.BE_hex(b'E5317801B3561125'): bin.hex(b'7DD051199F8401F95E4C03C884DCEA33')
               , bin.BE_hex(b'16B866D7BA3A8036'): bin.hex(b'1395E882BF25B481F61A4D621141DA6E')
               , bin.BE_hex(b'11131FFDA0D18D30'): bin.hex(b'C32AD1B82528E0A456897B3CE1C2D27E')
               , bin.BE_hex(b'CAC6B95B2724144A'): bin.hex(b'73E4BEA145DF2B89B65AEF02F83FA260')
               , bin.BE_hex(b'B7DBC693758A5C36'): bin.hex(b'BC3A92BFE302518D91CC30790671BF10')
               , bin.BE_hex(b'90CA73B2CDE3164B'): bin.hex(b'5CBFF11F22720BACC2AE6AAD8FE53317')
               , bin.BE_hex(b'6DD3212FB942714A'): bin.hex(b'E02C1643602EC16C3AE2A4D254A08FD9')
               , bin.BE_hex(b'11DDB470ABCBA130'): bin.hex(b'66198766B1C4AF7589EFD13AD4DD667A')
               , bin.BE_hex(b'5BEF27EEE95E0B4B'): bin.hex(b'36BCD2B551FF1C84AA3A3994CCEB033E')
               , bin.BE_hex(b'9359B46E49D2DA42'): bin.hex(b'173D65E7FCAE298A9363BD6AA189F200')
               , bin.BE_hex(b'1A46302EF8896F34'): bin.hex(b'8029AD5451D4BC18E9D0F5AC449DC055')
               , bin.BE_hex(b'693529F7D40A064C'): bin.hex(b'CE54873C62DAA48EFF27FCC032BD07E3')
               , bin.BE_hex(b'388B85AEEDCB685D'): bin.hex(b'D926E659D04A096B24C19151076D379A')
               , bin.BE_hex(b'FA505078126ACB3E'): bin.hex(b'BDC51862ABED79B2DE48C8E7E66C6200')
               , bin.BE_hex(b'FF813F7D062AC0BC'): bin.hex(b'AA0B5C77F088CCC2D39049BD267F066D')
               , bin.BE_hex(b'D1E9B5EDF9283668'): bin.hex(b'8E4A2579894E38B4AB9058BA5C7328EE')
               , bin.BE_hex(b'B76729641141CB34'): bin.hex(b'9849D1AA7B1FD09819C5C66283A326EC')
               , bin.BE_hex(b'FFB9469FF16E6BF8'): bin.hex(b'D514BD1909A9E5DC8703F4B8BB1DFD9A')
               , bin.BE_hex(b'23C5B5DF837A226C'): bin.hex(b'1406E2D873B6FC99217A180881DA8D62')
               , bin.BE_hex(b'E2854509C471C554'): bin.hex(b'433265F0CDEB2F4E65C0EE7008714D9E')
               , bin.BE_hex(b'8EE2CB82178C995A'): bin.hex(b'DA6AFC989ED6CAD279885992C037A8EE')
               , bin.BE_hex(b'5813810F4EC9B005'): bin.hex(b'01BE8B43142DD99A9E690FAD288B6082')
               , bin.BE_hex(b'7F9E217166ED43EA'): bin.hex(b'05FC927B9F4F5B05568142912A052B0F')
               , bin.BE_hex(b'C4A8D364D23793F7'): bin.hex(b'D1AC20FD14957FABC27196E9F6E7024A')
               , bin.BE_hex(b'40A234AEBCF2C6E5'): bin.hex(b'C6C5F6C7F735D7D94C87267FA4994D45')
               , bin.BE_hex(b'9CF7DFCFCBCE4AE5'): bin.hex(b'72A97A24A998E3A5500F3871F37628C0')
               , bin.BE_hex(b'4E4BDECAB8485B4F'): bin.hex(b'3832D7C42AAC9268F00BE7B6B48EC9AF')
               , bin.BE_hex(b'94A50AC54EFF70E4'): bin.hex(b'C2501A72654B96F86350C5A927962F7A')
               , bin.BE_hex(b'BA973B0E01DE1C2C'): bin.hex(b'D83BBCB46CC438B17A48E76C4F5654A3')
               , bin.BE_hex(b'494A6F8E8E108BEF'): bin.hex(b'F0FDE1D29B274F6E7DBDB7FF815FE910')
               , bin.BE_hex(b'918D6DD0C3849002'): bin.hex(b'857090D926BB28AEDA4BF028CACC4BA3')
               , bin.BE_hex(b'0B5F6957915ADDCA'): bin.hex(b'4DD0DC82B101C80ABAC0A4D57E67F859')
               , bin.BE_hex(b'794F25C6CD8AB62B'): bin.hex(b'76583BDACD5257A3F73D1598A2CA2D99')
               , bin.BE_hex(b'A9633A54C1673D21'): bin.hex(b'1F8D467F5D6D411F8A548B6329A5087E')
               , bin.BE_hex(b'5E5D896B3E163DEA'): bin.hex(b'8ACE8DB169E2F98AC36AD52C088E77C1')
               , bin.BE_hex(b'0EBE36B5010DFD7F'): bin.hex(b'9A89CC7E3ACB29CF14C60BC13B1E4616')
               , bin.BE_hex(b'01E828CFFA450C0F'): bin.hex(b'972B6E74420EC519E6F9D97D594AA37C')
               , bin.BE_hex(b'4A7BD170FE18E6AE'): bin.hex(b'AB55AE1BF0C7C519AFF028C15610A45B')
               , bin.BE_hex(b'69549CB975E87C4F'): bin.hex(b'7B6FA382E1FAD1465C851E3F4734A1B3')
               , bin.BE_hex(b'460C92C372B2A166'): bin.hex(b'946D5659F2FAF327C0B7EC828B748ADB')
               , bin.BE_hex(b'8165D801CCA11962'): bin.hex(b'CD0C0FFAAD9363EC14DD25ECDD2A5B62')
               , bin.BE_hex(b'A3F1C999090ADAC9'): bin.hex(b'B72FEF4A01488A88FF02280AA07A92BB')
               , bin.BE_hex(b'094E9A0474876B98'): bin.hex(b'E533BB6D65727A5832680D620B0BC10B')
               , bin.BE_hex(b'3DB25CB86A40335E'): bin.hex(b'02990B12260C1E9FDD73FE47CBAB7024')
               , bin.BE_hex(b'0DCD81945F4B4686'): bin.hex(b'1B789B87FB3C9238D528997BFAB44186')
               , bin.BE_hex(b'486A2A3A2803BE89'): bin.hex(b'32679EA7B0F99EBF4FA170E847EA439A')
               , bin.BE_hex(b'71F69446AD848E06'): bin.hex(b'E79AEB88B1509F628F38208201741C30')
               , bin.BE_hex(b'211FCD1265A928E9'): bin.hex(b'A736FBF58D587B3972CE154A86AE4540')
               , bin.BE_hex(b'0ADC9E327E42E98C'): bin.hex(b'017B3472C1DEE304FA0B2FF8E53FF7D6')
               , bin.BE_hex(b'BAE9F621B60174F1'): bin.hex(b'38C3FB39B4971760B4B982FE9F095014')
               , bin.BE_hex(b'34DE1EEADC97115E'): bin.hex(b'2E3A53D59A491E5CD173F337F7CD8C61')
               , bin.BE_hex(b'E07E107F1390A3DF'): bin.hex(b'290D27B0E871F8C5B14A14E514D0F0D9')
               , bin.BE_hex(b'32690BF74DE12530'): bin.hex(b'A2556210AE5422E6D61EDAAF122CB637')
               , bin.BE_hex(b'BF3734B1DCB04696'): bin.hex(b'48946123050B00A7EFB1C029EE6CC438')
               , bin.BE_hex(b'74F4F78002A5A1BE'): bin.hex(b'C14EEC8D5AEEF93FA811D450B4E46E91')
               , bin.BE_hex(b'B1EB52A64BFAF7BF'): bin.hex(b'458133AA43949A141632C4F8596DE2B0')
               , bin.BE_hex(b'FC6F20EE98D208F6'): bin.hex(b'57790E48D35500E70DF812594F507BE7')
               , bin.BE_hex(b'402CFABF2020D9B7'): bin.hex(b'67197BCD9D0EF0C4085378FAA69A3264')
               , bin.BE_hex(b'6FA0420E902B4FBE'): bin.hex(b'27B750184E5329C4E4455CBD3E1FD5AB')
               , bin.BE_hex(b'2C547F26A2613E01'): bin.hex(b'37C50C102D4C9E3A5AC069F072B1417D')
               }

class mode_salsa20:
  def __init__(self, keyname):
    if (len (keyname) != 8):
      raise Exception("salsa20 keyname length shall be 8. keyname={}".format(keyname))
    self.keyname = keyname
    
  def __call__(self, data):
    iv = secrets.token_bytes(4)
    inner = mode_normal()(data)
    return ( b'E'
           + bin.uint8_t (len (self.keyname)) # key_name_length
           + self.keyname                     # key_name
           + bin.uint8_t (len (iv))           # iv_length
           + iv                               # iv
           + b'S'                             # type
           + salsa20.Salsa20 (salsa20_keys[self.keyname], iv, 20).encrypt (inner)
           )
           
def encode_dumb(data, mode = None):
  if not mode:
    mode = mode_salsa20(random.choice(list(salsa20_keys.keys())))
    #mode = mode_normal()
  return ( b'BLTE'             # magic
         + bin.BE_uint32_t (0) # headerSize
         + mode(data)
         )

def encode_file_dumb(file, output):
  with open(file, u"rb") as f:
    data = f.read()
  with open(output, u"wb+") as f:
    f.write(encode_dumb(data))
    
if __name__ == '__main__':
  encode_file_dumb(sys.argv[1], sys.argv[2])
