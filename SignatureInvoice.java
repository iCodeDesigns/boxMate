// 
// Decompiled by Procyon v0.5.36
// 

package arkleap.apps.ar.inv.model;
import py4j.*;
import java.util.ArrayList;
import java.util.List;
import org.codehaus.jettison.json.JSONArray;
import java.text.DecimalFormat;
import java.util.HashMap;
import org.codehaus.jettison.json.JSONException;
import org.codehaus.jettison.json.JSONObject;
import java.util.Map;
import java.security.NoSuchAlgorithmException;
import org.bouncycastle.util.Store;
import java.util.Iterator;
import org.bouncycastle.cms.SignerInformationStore;
import org.bouncycastle.cms.CMSTypedData;
import org.bouncycastle.cms.CMSSignedData;
import org.bouncycastle.cms.CMSProcessable;
import org.bouncycastle.operator.DigestCalculatorProvider;
import java.util.Set;
import java.io.IOException;
import java.io.Writer;
import java.io.BufferedWriter;
import java.io.FileWriter;
import org.bouncycastle.operator.OperatorCreationException;
import org.bouncycastle.cms.jcajce.JcaSimpleSignerInfoVerifierBuilder;
import org.bouncycastle.cert.jcajce.JcaX509CertificateConverter;
import org.bouncycastle.cert.X509CertificateHolder;
import org.bouncycastle.util.Selector;
import org.bouncycastle.cms.SignerInformation;
import java.util.Arrays;
import java.io.OutputStream;
import org.bouncycastle.asn1.DEROutputStream;
import java.io.FileOutputStream;
import org.bouncycastle.asn1.ASN1InputStream;
import java.util.Base64;
import org.bouncycastle.cms.CMSException;
import org.bouncycastle.cms.CMSAttributeTableGenerator;
import org.bouncycastle.cms.CMSProcessableByteArray;
import org.bouncycastle.cms.CMSSignedDataGenerator;
import java.security.cert.CertStoreParameters;
import java.security.cert.CertStore;
import java.util.Collection;
import java.security.cert.CollectionCertStoreParameters;
import java.util.Collections;
import org.bouncycastle.cms.DefaultSignedAttributeTableGenerator;
import org.bouncycastle.asn1.cms.AttributeTable;
import org.bouncycastle.operator.jcajce.JcaDigestCalculatorProviderBuilder;
import org.bouncycastle.asn1.ASN1EncodableVector;
import java.nio.charset.StandardCharsets;
import org.bouncycastle.asn1.DEROctetString;
import org.bouncycastle.asn1.cms.CMSAttributes;
import org.bouncycastle.asn1.ASN1Set;
import org.bouncycastle.asn1.cms.Attribute;
import org.bouncycastle.asn1.ASN1Encodable;
import org.bouncycastle.asn1.DERSet;
import org.bouncycastle.asn1.pkcs.PKCSObjectIdentifiers;
import org.bouncycastle.asn1.ess.SigningCertificateV2;
import org.bouncycastle.asn1.ess.ESSCertIDv2;
import org.bouncycastle.asn1.x509.AlgorithmIdentifier;
import org.bouncycastle.asn1.nist.NISTObjectIdentifiers;
import java.security.MessageDigest;
import java.security.cert.X509Certificate;
import java.security.PrivateKey;
import java.util.Enumeration;
import java.security.Security;
import sun.security.pkcs11.SunPKCS11;
import java.io.ByteArrayInputStream;
import java.security.Provider;
import java.security.Key;
import java.security.cert.Certificate;
import java.security.KeyStore;
import java.io.InputStream;

    public class SignatureInvoice
{
    protected String providerName;
    protected String library;
    protected InputStream providerConfig;
    protected char[] passwordKeystore;
    protected KeyStore keyStore;
    protected String alias_Auth;
    protected Certificate certificate_Auth;
    protected Key privateKey_Auth;
    protected String alias_Sign;
    protected Certificate certificate_Sign;
    protected Key privateKey_Sign;
    protected String Serlized_s;
    protected String x;
    protected Provider providerPKCS11;
    static String response;
    
    public SignatureInvoice() {
        this.x = "";
    }
    
    public SignatureInvoice(final String library, final String pin) throws Exception {
        this(library, "token", pin);
    }
    
    public SignatureInvoice(final String library, final String providerName, final String pin) throws Exception {
        this.x = "";
        this.providerName = providerName;
        this.library = library;
        System.out.println("1");
        final String pkcs11Config = "name=" + providerName + "\nlibrary=" + System.getProperty("user.dir") + "/eps2003csp11.dll";
        System.out.println("pkcs11Config" + pkcs11Config);
        final ByteArrayInputStream pkcs11ConfigStream = new ByteArrayInputStream(pkcs11Config.getBytes());
        Security.addProvider(this.providerPKCS11 = new SunPKCS11((InputStream)pkcs11ConfigStream));
        this.passwordKeystore = pin.toCharArray();
        System.out.println("passwordKeystore" + (Object)this.passwordKeystore);
        (this.keyStore = KeyStore.getInstance("PKCS11", this.providerPKCS11)).load(null, this.passwordKeystore);
        final Enumeration<String> aliases = this.keyStore.aliases();
        System.out.println(aliases + "aliases");
        final String alias = null;
        if (aliases.hasMoreElements()) {
            this.alias_Auth = aliases.nextElement();
        }
        if (aliases.hasMoreElements()) {
            this.alias_Sign = aliases.nextElement();
        }
        if (this.alias_Sign == null) {
            this.alias_Sign = this.alias_Auth;
        }
        this.certificate_Auth = this.keyStore.getCertificate(this.alias_Auth);
        this.privateKey_Auth = this.keyStore.getKey(this.alias_Auth, this.passwordKeystore);
        this.certificate_Auth = this.keyStore.getCertificate(this.alias_Auth);
        this.privateKey_Auth = this.keyStore.getKey(this.alias_Auth, this.passwordKeystore);
    }
    
    public PrivateKey getPrivateKeyAuth() throws Exception {
        if (this.privateKey_Auth instanceof PrivateKey) {
            return (PrivateKey)this.privateKey_Auth;
        }
        return null;
    }
    
    public X509Certificate getX509CertificateAuth() throws Exception {
        if (this.certificate_Auth instanceof X509Certificate) {
            return (X509Certificate)this.certificate_Auth;
        }
        return null;
    }
    
    public PrivateKey getPrivateKeySign() throws Exception {
        if (this.privateKey_Sign instanceof PrivateKey) {
            return (PrivateKey)this.privateKey_Sign;
        }
        if (this.alias_Sign == null || this.keyStore == null) {
            return null;
        }
        this.privateKey_Sign = this.keyStore.getKey(this.alias_Sign, this.passwordKeystore);
        if (this.privateKey_Sign instanceof PrivateKey) {
            return (PrivateKey)this.privateKey_Sign;
        }
        return null;
    }
    
    public X509Certificate getX509CertificateSign() throws Exception {
        if (this.certificate_Sign instanceof X509Certificate) {
            return (X509Certificate)this.certificate_Sign;
        }
        if (this.alias_Sign == null || this.keyStore == null) {
            return null;
        }
        this.certificate_Sign = this.keyStore.getCertificate(this.alias_Sign);
        if (this.certificate_Sign instanceof X509Certificate) {
            return (X509Certificate)this.certificate_Sign;
        }
        return null;
    }
    
    public byte[] sign(final String content) throws Exception {
        final byte[] hashed = this.getHashed(this.x);
        final MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
        final byte[] digestedCert = sha256.digest(this.getX509CertificateSign().getEncoded());
        final AlgorithmIdentifier aiSha256 = new AlgorithmIdentifier(NISTObjectIdentifiers.id_sha256);
        final ESSCertIDv2 essCert1 = new ESSCertIDv2(aiSha256, digestedCert);
        final ESSCertIDv2[] essCert1Arr = { essCert1 };
        final SigningCertificateV2 scv2 = new SigningCertificateV2(essCert1Arr);
        final Attribute certHAttribute = new Attribute(PKCSObjectIdentifiers.id_aa_signingCertificateV2, (ASN1Set)new DERSet((ASN1Encodable)scv2));
        final Attribute MessageDigestAttribute = new Attribute(CMSAttributes.messageDigest, (ASN1Set)new DERSet((ASN1Encodable)new DEROctetString(hashed)));
        final Attribute MessageDigestAttribute2 = new Attribute(PKCSObjectIdentifiers.digestedData, (ASN1Set)new DERSet((ASN1Encodable)new DEROctetString(this.x.getBytes(StandardCharsets.UTF_8))));
        final Set<Provider.Service> services = this.providerPKCS11.getServices();
        services.forEach(service -> System.out.println(service.getAlgorithm()));
        final ASN1EncodableVector asn1EncodableVector = new ASN1EncodableVector();
        asn1EncodableVector.add((ASN1Encodable)certHAttribute);
        asn1EncodableVector.add((ASN1Encodable)MessageDigestAttribute);
        asn1EncodableVector.add((ASN1Encodable)MessageDigestAttribute2);
        final DigestCalculatorProvider dcp = new JcaDigestCalculatorProviderBuilder().setProvider(this.providerPKCS11).build();
        System.out.println(dcp.get(aiSha256));
        final AttributeTable attributeTable = new AttributeTable(asn1EncodableVector);
        final CMSAttributeTableGenerator attrGen = (CMSAttributeTableGenerator)new DefaultSignedAttributeTableGenerator(attributeTable);
        final CertStore certStore = CertStore.getInstance("Collection", new CollectionCertStoreParameters(Collections.singletonList(this.getX509CertificateSign())));
        final CMSSignedDataGenerator generator = new CMSSignedDataGenerator();
        final CMSProcessable cmsProcessable = (CMSProcessable)new CMSProcessableByteArray(PKCSObjectIdentifiers.digestedData, this.x.getBytes(StandardCharsets.UTF_8));
        System.out.println(PKCSObjectIdentifiers.digestedData + "dddd");
        System.out.println(this.getX509CertificateSign().getSubjectX500Principal() + "testttt" + this.getX509CertificateSign().getSerialNumber());
        System.out.println("NISTObjectIdentifiers.id_sha256" + NISTObjectIdentifiers.id_sha256 + "kk" + NISTObjectIdentifiers.id_sha256.getId());
        generator.addCertificatesAndCRLs(certStore);
        generator.addSigner(this.getPrivateKeyAuth(), this.getX509CertificateSign(), NISTObjectIdentifiers.id_sha256.getId(), attrGen, (CMSAttributeTableGenerator)null);
        CMSSignedData signedData = null;
        final CMSTypedData msg = (CMSTypedData)new CMSProcessableByteArray(hashed);
        try {
            signedData = generator.generate(cmsProcessable, false, this.providerPKCS11);
        }
        catch (CMSException ex) {}
        final byte[] abPKCS7Signature = signedData.getEncoded();
        Base64.getEncoder().encode(abPKCS7Signature);
        Base64.getDecoder().decode(Base64.getEncoder().encode(abPKCS7Signature));
        System.out.println(Base64.getEncoder().encodeToString(abPKCS7Signature));
        final ASN1InputStream asn1 = new ASN1InputStream(signedData.getEncoded());
        final FileOutputStream fos = new FileOutputStream(System.getProperty("user.dir") + "\\pathJAR.der");
        final DEROutputStream dos = new DEROutputStream((OutputStream)fos);
        dos.writeObject((ASN1Encodable)asn1.readObject());
        dos.flush();
        dos.close();
        asn1.close();
        System.out.println("hased" + Arrays.toString(hashed));
        System.out.println("hh" + Arrays.toString((byte[])signedData.getSignedContent().getContent()));
        final SignerInformationStore signers = signedData.getSignerInfos();
        final Collection c = signers.getSigners();
        final Iterator it = c.iterator();
        final Store store1 = signedData.getCertificates();
        while (it.hasNext()) {
            final SignerInformation signer = it.next();
            System.out.println("dd=" + signer.getDigestAlgorithmID().getAlgorithm() + "\nsigned");
            signer.verify(this.getX509CertificateSign(), this.providerPKCS11);
            final AttributeTable attributes = signer.getSignedAttributes();
            final Attribute attribute2 = signer.getSignedAttributes().get(PKCSObjectIdentifiers.pkcs_9_at_messageDigest);
            final ASN1Encodable value = (ASN1Encodable)attribute2.getAttrValues();
            final Attribute attribute3 = attributes.get(PKCSObjectIdentifiers.digestedData);
            System.out.println(attribute3.getAttrValues().parser().readObject());
            System.out.println("dd=" + new DERSet((ASN1Encodable)new DEROctetString(hashed)));
            final Collection certCollection = store1.getMatches((Selector)signer.getSID());
            final Iterator certIt = certCollection.iterator();
            System.out.println(store1.getMatches((Selector)null) + "collection of certs");
            while (certIt.hasNext()) {
                System.out.println("enter while loop2");
                final X509CertificateHolder certHolder = certIt.next();
                final X509Certificate certr = new JcaX509CertificateConverter().getCertificate(certHolder);
                System.out.println("od" + Arrays.toString(certr.getSignature()));
                try {
                    if (signer.verify(new JcaSimpleSignerInfoVerifierBuilder().build(certr))) {
                        System.out.println("verified correct");
                    }
                    else {
                        System.out.println("not verified");
                    }
                }
                catch (OperatorCreationException ex2) {}
            }
        }
        final String str = Base64.getEncoder().encodeToString(abPKCS7Signature);
        System.out.println(Base64.getEncoder().encodeToString(abPKCS7Signature));
        try {
            final BufferedWriter writer = new BufferedWriter(new FileWriter(System.getProperty("user.dir") + "\\Cadesbes.txt"));
            writer.write(str);
            writer.close();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        return abPKCS7Signature;
    }
    
    public String getFullSigature(final String content, final String sig) {
        System.out.println("substr=" + content.substring(0, content.lastIndexOf("}") - 1));
        final String y = "{\n    \"documents\": [\n" + content.substring(0, content.lastIndexOf("}") - 1) + ",\n            \"signatures\": [\n                {\n                    \"signatureType\": \"I\",\"value\":\"" + sig + "\"\n                }\n            ]\n        }\n    ]\t\n}";
        try {
            final BufferedWriter writer = new BufferedWriter(new FileWriter(System.getProperty("user.dir") + "\\FullSignature.json"));
            writer.write(y);
            writer.close();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        return y;
    }
    
    public byte[] getHashed(final String ser) {
        byte[] hashed = null;
        try {
            final MessageDigest md = MessageDigest.getInstance("SHA-256");
            hashed = md.digest(ser.getBytes(StandardCharsets.UTF_8));
        }
        catch (NoSuchAlgorithmException e) {
            System.out.println("digesterror");
            e.printStackTrace();
        }
        return hashed;
    }
    
    public Map<String, Object> jsonToMap(final Object json) throws JSONException {
        if (json instanceof JSONObject) {
            return this._jsonToMap_((JSONObject)json);
        }
        if (json instanceof String) {
            final JSONObject jsonObject = new JSONObject((String)json);
            return this._jsonToMap_(jsonObject);
        }
        return null;
    }
    
    private Map<String, Object> _jsonToMap_(final JSONObject json) throws JSONException {
        Map<String, Object> retMap = new HashMap<String, Object>();
        if (json != JSONObject.NULL) {
            retMap = this.toMap(json);
        }
        return retMap;
    }
    
    private Map<String, Object> toMap(final JSONObject object) throws JSONException {
        final Map<String, Object> map = new HashMap<String, Object>();
        final Iterator<String> keysItr = (Iterator<String>)object.keys();
        System.out.println(keysItr.hasNext());
        while (keysItr.hasNext()) {
            final String key = keysItr.next();
            Object value = object.get(key);
            this.x = this.x + "\"" + key.toUpperCase() + "\"";
            if (value instanceof Double) {
                final String x1 = String.valueOf(object.get(key));
                System.out.println(new DecimalFormat("#.#####").format(value) + "x1" + x1 + object.get(key).toString() + "length" + object.getLong(key));
                final Double newData = new Double((double)value);
                if (key.equals("rate") && object.get(key).toString().contains(".")) {
                    final String s = String.format("%.2f", newData);
                    System.out.println(s + "s");
                    value = s;
                }
                else {
                    final String s = String.format("%.5f", newData);
                    System.out.println(s + "s");
                    value = s;
                }
            }
            if (value instanceof JSONArray) {
                value = this.toList((JSONArray)value, key.toUpperCase());
            }
            else if (value instanceof JSONObject) {
                System.out.println("tomap");
                value = this.toMap((JSONObject)value);
            }
            else {
                this.x = this.x + "\"" + value.toString() + "\"";
            }
            map.put(key, value);
        }
        return map;
    }
    
    public List<Object> toList(final JSONArray array, final String key) throws JSONException {
        final List<Object> list = new ArrayList<Object>();
        for (int i = 0; i < array.length(); ++i) {
            Object value = array.get(i);
            this.x = this.x + "\"" + key.toUpperCase() + "\"";
            if (value instanceof JSONArray) {
                value = this.toList((JSONArray)value, key);
            }
            else if (value instanceof JSONObject) {
                value = this.toMap((JSONObject)value);
            }
            list.add(value);
        }
        return list;
    }
    
    public void createSerlizationFile() {
        try {
            final BufferedWriter writer = new BufferedWriter(new FileWriter(System.getProperty("user.dir") + "\\CanonicalString.txt"));
            writer.write(this.x);
            writer.close();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        System.out.println("lengthofx=" + this.x.length() + "x=" + this.x);
    }
    
    public void FullSigatureDocuments() {
        try {
            final BufferedWriter writer = new BufferedWriter(new FileWriter(System.getProperty("user.dir") + "\\CanonicalString.txt"));
            writer.write(this.x);
            writer.close();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        System.out.println("lengthofx=" + this.x.length() + "x=" + this.x);
    }
    
    public static void main(final String[] args) {
        GatewayServer server = new GatewayServer(new SignatureInvoice());
        final String h = getFullSignedDocument(SignatureInvoice.response, "Dreem", "08268939");
        System.out.println("hvalueis" + h);
    }
    
    public static String getFullSignedDocument(final String json, final String Token, final String pin) {
        try {
            final SignatureInvoice s = new SignatureInvoice(null, Token, pin);
            s.jsonToMap(json);
            s.createSerlizationFile();
            s.getHashed(s.x);
            final byte[] b = s.sign(s.x);
            return s.getFullSigature(json, Base64.getEncoder().encodeToString(b));
        }
        catch (Exception ex) {
            return null;
        }
    }
    
    static {
        SignatureInvoice.response = "        {\n            \"issuer\": {\n                \"address\": {\n                    \"branchID\": \"0\",\n                    \"country\": \"EG\",\n                    \"governate\": \"Cairo\",\n                    \"regionCity\": \"Nasr City\",\n                    \"street\": \"580 Clementina Key\",\n                    \"buildingNumber\": \"Bldg. 0\",\n                    \"postalCode\": \"68030\",\n                    \"floor\": \"1\",\n                    \"room\": \"123\",\n                    \"landmark\": \"7660 Melody Trail\",\n                    \"additionalInformation\": \"beside Townhall\"\n                },\n                \"type\": \"B\",\n                \"id\": \"100324932\",\n                \"name\": \"Dreem\"\n            },\n            \"receiver\": {\n                \"address\": {\n                    \"country\": \"EG\",\n                    \"governate\": \"Egypt\",\n                    \"regionCity\": \"Mufazat al Ismlyah\",\n                    \"street\": \"580 Clementina Key\",\n                    \"buildingNumber\": \"Bldg. 0\",\n                    \"postalCode\": \"68030\",\n                    \"floor\": \"1\",\n                    \"room\": \"123\",\n                    \"landmark\": \"7660 Melody Trail\",\n                    \"additionalInformation\": \"beside Townhall\"\n                },\n                \"type\": \"B\",\n                \"id\": \"313717919\",\n                \"name\": \"Receiver\"\n            },\n            \"documentType\": \"I\",\n            \"documentTypeVersion\": \"1.0\",\n            \"dateTimeIssued\": \"2021-02-14T02:04:45Z\",\n            \"taxpayerActivityCode\": \"1079\",\n            \"internalID\": \"AR-00022\",\n            \"purchaseOrderReference\": \"P-233-A6375\",\n            \"purchaseOrderDescription\": \"purchase Order description\",\n            \"salesOrderReference\": \"1231\",\n            \"salesOrderDescription\": \"Sales Order description\",\n            \"proformaInvoiceNumber\": \"SomeValue\",\n            \"payment\": {\n                \"bankName\": \"SomeValue\",\n                \"bankAddress\": \"SomeValue\",\n                \"bankAccountNo\": \"SomeValue\",\n                \"bankAccountIBAN\": \"\",\n                \"swiftCode\": \"\",\n                \"terms\": \"SomeValue\"\n            },\n            \"invoiceLines\": [\n                {\n                    \"description\": \"Fruity Machine\",\n                    \"itemType\": \"EGS\",\n                    \"itemCode\": \"EG-100324932-11111\",\n                    \"unitType\": \"EA\",\n                    \"quantity\": 7.00000,\n                    \"internalCode\": \"FSPM001\",\n                    \"salesTotal\": 662.90000,\n                    \"total\": 2220.08914,\n                    \"valueDifference\": 7.00000,\n                    \"totalTaxableFees\": 618.69212,\n                    \"netTotal\": 649.64200,\n                    \"itemsDiscount\": 5.00000,\n                    \"unitValue\": {\n                        \"currencySold\": \"USD\",\n                        \"amountEGP\": 94.70000,\n                        \"amountSold\": 4.73500,\n                        \"currencyExchangeRate\": 20.00000\n                    },\n                    \"discount\": {\n                        \"rate\": 2,\n                        \"amount\": 13.25800\n                    },\n                    \"taxableItems\": [\n                        {\n                            \"taxType\": \"T1\",\n                            \"amount\": 204.67639,\n                            \"subType\": \"V001\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T2\",\n                            \"amount\": 156.64009,\n                            \"subType\": \"Tbl01\",\n                            \"rate\": 12\n                        },\n                        {\n                            \"taxType\": \"T3\",\n                            \"amount\": 30.00000,\n                            \"subType\": \"Tbl02\",\n                            \"rate\": 0.00\n                        },\n                        {\n                            \"taxType\": \"T4\",\n                            \"amount\": 32.23210,\n                            \"subType\": \"W001\",\n                            \"rate\": 5.00\n                        },\n                        {\n                            \"taxType\": \"T5\",\n                            \"amount\": 90.94988,\n                            \"subType\": \"ST01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T6\",\n                            \"amount\": 60.00000,\n                            \"subType\": \"ST02\",\n                            \"rate\": 0.00\n                        },\n                        {\n                            \"taxType\": \"T7\",\n                            \"amount\": 64.96420,\n                            \"subType\": \"Ent01\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T8\",\n                            \"amount\": 90.94988,\n                            \"subType\": \"RD01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T9\",\n                            \"amount\": 77.95704,\n                            \"subType\": \"SC01\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T10\",\n                            \"amount\": 64.96420,\n                            \"subType\": \"Mn01\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T11\",\n                            \"amount\": 90.94988,\n                            \"subType\": \"MI01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T12\",\n                            \"amount\": 77.95704,\n                            \"subType\": \"OF01\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T13\",\n                            \"amount\": 64.96420,\n                            \"subType\": \"ST03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T14\",\n                            \"amount\": 90.94988,\n                            \"subType\": \"ST04\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T15\",\n                            \"amount\": 77.95704,\n                            \"subType\": \"Ent03\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T16\",\n                            \"amount\": 64.96420,\n                            \"subType\": \"RD03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T17\",\n                            \"amount\": 64.96420,\n                            \"subType\": \"SC03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T18\",\n                            \"amount\": 90.94988,\n                            \"subType\": \"Mn03\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T19\",\n                            \"amount\": 77.95704,\n                            \"subType\": \"MI03\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T20\",\n                            \"amount\": 64.96420,\n                            \"subType\": \"OF03\",\n                            \"rate\": 10.00\n                        }\n                    ]\n                },\n                {\n                    \"description\": \"EG-100324932-002\",\n                    \"itemType\": \"EGS\",\n                    \"itemCode\": \"EG-100324932-002\",\n                    \"unitType\": \"EA\",\n                    \"quantity\": 5.00000,\n                    \"internalCode\": \"FSPM002\",\n                    \"salesTotal\": 947.00000,\n                    \"total\": 3123.51323,\n                    \"valueDifference\": 7.00000,\n                    \"totalTaxableFees\": 858.13160,\n                    \"netTotal\": 928.06000,\n                    \"itemsDiscount\": 5.00000,\n                    \"unitValue\": {\n                        \"currencySold\": \"EUR\",\n                        \"amountEGP\": 189.40000,\n                        \"amountSold\": 10.00000,\n                        \"currencyExchangeRate\": 18.94000\n                    },\n                    \"discount\": {\n                        \"rate\": 2,\n                        \"amount\": 18.94000\n                    },\n                    \"taxableItems\": [\n                        {\n                            \"taxType\": \"T1\",\n                            \"amount\": 285.87644,\n                            \"subType\": \"V001\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T2\",\n                            \"amount\": 218.78299,\n                            \"subType\": \"Tbl01\",\n                            \"rate\": 12\n                        },\n                        {\n                            \"taxType\": \"T3\",\n                            \"amount\": 30.00000,\n                            \"subType\": \"Tbl02\",\n                            \"rate\": 0.00\n                        },\n                        {\n                            \"taxType\": \"T4\",\n                            \"amount\": 46.15300,\n                            \"subType\": \"W001\",\n                            \"rate\": 5.00\n                        },\n                        {\n                            \"taxType\": \"T5\",\n                            \"amount\": 129.92840,\n                            \"subType\": \"ST01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T6\",\n                            \"amount\": 60.00000,\n                            \"subType\": \"ST02\",\n                            \"rate\": 0.00\n                        },\n                        {\n                            \"taxType\": \"T7\",\n                            \"amount\": 92.80600,\n                            \"subType\": \"Ent01\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T8\",\n                            \"amount\": 129.92840,\n                            \"subType\": \"RD01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T9\",\n                            \"amount\": 111.36720,\n                            \"subType\": \"SC01\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T10\",\n                            \"amount\": 92.80600,\n                            \"subType\": \"Mn01\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T11\",\n                            \"amount\": 129.92840,\n                            \"subType\": \"MI01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T12\",\n                            \"amount\": 111.36720,\n                            \"subType\": \"OF01\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T13\",\n                            \"amount\": 92.80600,\n                            \"subType\": \"ST03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T14\",\n                            \"amount\": 129.92840,\n                            \"subType\": \"ST04\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T15\",\n                            \"amount\": 111.36720,\n                            \"subType\": \"Ent03\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T16\",\n                            \"amount\": 92.80600,\n                            \"subType\": \"RD03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T17\",\n                            \"amount\": 92.80600,\n                            \"subType\": \"SC03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T18\",\n                            \"amount\": 129.92840,\n                            \"subType\": \"Mn03\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T19\",\n                            \"amount\": 111.36720,\n                            \"subType\": \"MI04\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T20\",\n                            \"amount\": 92.80600,\n                            \"subType\": \"OF03\",\n                            \"rate\": 10.00\n                        }\n                    ]\n                },\n                {\n                    \"description\": \"EG-100324932-003\",\n                    \"itemType\": \"EGS\",\n                    \"itemCode\": \"EG-100324932-003\",\n                    \"unitType\": \"EA\",\n                    \"quantity\": 6.57265,\n                    \"internalCode\": \"FSPM003\",\n                    \"salesTotal\": 1445.98300,\n                    \"total\": 4522.41770,\n                    \"valueDifference\": 3.00000,\n                    \"totalTaxableFees\": 1228.93264,\n                    \"netTotal\": 1359.22402,\n                    \"itemsDiscount\": 4.00000,\n                    \"unitValue\": {\n                        \"currencySold\": \"USD\",\n                        \"amountEGP\": 220.00000,\n                        \"amountSold\": 11.00000,\n                        \"currencyExchangeRate\": 20.00000\n                    },\n                    \"discount\": {\n                        \"rate\": 6,\n                        \"amount\": 86.75898\n                    },\n                    \"taxableItems\": [\n                        {\n                            \"taxType\": \"T1\",\n                            \"amount\": 410.99736,\n                            \"subType\": \"V001\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T2\",\n                            \"amount\": 314.53880,\n                            \"subType\": \"Tbl01\",\n                            \"rate\": 12\n                        },\n                        {\n                            \"taxType\": \"T3\",\n                            \"amount\": 30.00000,\n                            \"subType\": \"Tbl02\",\n                            \"rate\": 0.00\n                        },\n                        {\n                            \"taxType\": \"T4\",\n                            \"amount\": 67.76120,\n                            \"subType\": \"W001\",\n                            \"rate\": 5.00\n                        },\n                        {\n                            \"taxType\": \"T5\",\n                            \"amount\": 190.29136,\n                            \"subType\": \"ST01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T6\",\n                            \"amount\": 60.00000,\n                            \"subType\": \"ST02\",\n                            \"rate\": 0.00\n                        },\n                        {\n                            \"taxType\": \"T7\",\n                            \"amount\": 135.92240,\n                            \"subType\": \"Ent01\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T8\",\n                            \"amount\": 190.29136,\n                            \"subType\": \"RD01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T9\",\n                            \"amount\": 163.10688,\n                            \"subType\": \"SC01\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T10\",\n                            \"amount\": 135.92240,\n                            \"subType\": \"Mn01\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T11\",\n                            \"amount\": 190.29136,\n                            \"subType\": \"MI01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T12\",\n                            \"amount\": 163.10688,\n                            \"subType\": \"OF01\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T13\",\n                            \"amount\": 135.92240,\n                            \"subType\": \"ST03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T14\",\n                            \"amount\": 190.29136,\n                            \"subType\": \"ST04\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T15\",\n                            \"amount\": 163.10688,\n                            \"subType\": \"Ent03\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T16\",\n                            \"amount\": 135.92240,\n                            \"subType\": \"RD03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T17\",\n                            \"amount\": 135.92240,\n                            \"subType\": \"SC03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T18\",\n                            \"amount\": 190.29136,\n                            \"subType\": \"Mn03\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T19\",\n                            \"amount\": 163.10688,\n                            \"subType\": \"MI04\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T20\",\n                            \"amount\": 135.92240,\n                            \"subType\": \"OF03\",\n                            \"rate\": 10.00\n                        }\n                    ]\n                },\n                {\n                    \"description\": \"EG-100324932-004\",\n                    \"itemType\": \"EGS\",\n                    \"itemCode\": \"EG-100324932-004\",\n                    \"unitType\": \"EA\",\n                    \"quantity\": 9.00000,\n                    \"internalCode\": \"FSPM004\",\n                    \"salesTotal\": 1363.68000,\n                    \"total\": 4221.86535,\n                    \"valueDifference\": 8.00000,\n                    \"totalTaxableFees\": 1150.67128,\n                    \"netTotal\": 1268.22240,\n                    \"itemsDiscount\": 11.00000,\n                    \"unitValue\": {\n                        \"currencySold\": \"EUR\",\n                        \"amountEGP\": 151.52000,\n                        \"amountSold\": 8.00000,\n                        \"currencyExchangeRate\": 18.94000\n                    },\n                    \"discount\": {\n                        \"rate\": 7,\n                        \"amount\": 95.45760\n                    },\n                    \"taxableItems\": [\n                        {\n                            \"taxType\": \"T1\",\n                            \"amount\": 385.24093,\n                            \"subType\": \"V001\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T2\",\n                            \"amount\": 294.82724,\n                            \"subType\": \"Tbl01\",\n                            \"rate\": 12\n                        },\n                        {\n                            \"taxType\": \"T3\",\n                            \"amount\": 30.00000,\n                            \"subType\": \"Tbl02\",\n                            \"rate\": 0.00\n                        },\n                        {\n                            \"taxType\": \"T4\",\n                            \"amount\": 62.86112,\n                            \"subType\": \"W001\",\n                            \"rate\": 5.00\n                        },\n                        {\n                            \"taxType\": \"T5\",\n                            \"amount\": 177.55114,\n                            \"subType\": \"ST01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T6\",\n                            \"amount\": 60.00000,\n                            \"subType\": \"ST02\",\n                            \"rate\": 0.00\n                        },\n                        {\n                            \"taxType\": \"T7\",\n                            \"amount\": 126.82224,\n                            \"subType\": \"Ent01\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T8\",\n                            \"amount\": 177.55114,\n                            \"subType\": \"RD01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T9\",\n                            \"amount\": 152.18669,\n                            \"subType\": \"SC01\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T10\",\n                            \"amount\": 126.82224,\n                            \"subType\": \"Mn01\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T11\",\n                            \"amount\": 177.55114,\n                            \"subType\": \"MI01\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T12\",\n                            \"amount\": 152.18669,\n                            \"subType\": \"OF01\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T13\",\n                            \"amount\": 126.82224,\n                            \"subType\": \"ST03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T14\",\n                            \"amount\": 177.55114,\n                            \"subType\": \"ST04\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T15\",\n                            \"amount\": 152.18669,\n                            \"subType\": \"Ent03\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T16\",\n                            \"amount\": 126.82224,\n                            \"subType\": \"RD03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T17\",\n                            \"amount\": 126.82224,\n                            \"subType\": \"SC03\",\n                            \"rate\": 10.00\n                        },\n                        {\n                            \"taxType\": \"T18\",\n                            \"amount\": 177.55114,\n                            \"subType\": \"Mn03\",\n                            \"rate\": 14.00\n                        },\n                        {\n                            \"taxType\": \"T19\",\n                            \"amount\": 152.18669,\n                            \"subType\": \"MI04\",\n                            \"rate\": 12.00\n                        },\n                        {\n                            \"taxType\": \"T20\",\n                            \"amount\": 126.82224,\n                            \"subType\": \"OF03\",\n                            \"rate\": 10.00\n                        }\n                    ]\n                }\n            ],\n            \"totalDiscountAmount\": 214.41458,\n            \"totalSalesAmount\": 4419.56300,\n            \"netAmount\": 4205.14842,\n            \"taxTotals\": [\n                {\n                    \"taxType\": \"T1\",\n                    \"amount\": 1286.79112\n                },\n                {\n                    \"taxType\": \"T2\",\n                    \"amount\": 984.78912\n                },\n                {\n                    \"taxType\": \"T3\",\n                    \"amount\": 120.00000\n                },\n                {\n                    \"taxType\": \"T4\",\n                    \"amount\": 209.00742\n                },\n                {\n                    \"taxType\": \"T5\",\n                    \"amount\": 588.72078\n                },\n                {\n                    \"taxType\": \"T6\",\n                    \"amount\": 240.00000\n                },\n                {\n                    \"taxType\": \"T7\",\n                    \"amount\": 420.51484\n                },\n                {\n                    \"taxType\": \"T8\",\n                    \"amount\": 588.72078\n                },\n                {\n                    \"taxType\": \"T9\",\n                    \"amount\": 504.61781\n\n                },\n                {\n                    \"taxType\": \"T10\",\n                    \"amount\": 420.51484\n                },\n                {\n                    \"taxType\": \"T11\",\n                    \"amount\": 588.72078\n                },\n                {\n                    \"taxType\": \"T12\",\n                    \"amount\": 504.61781\n                },\n                {\n                    \"taxType\": \"T13\",\n                    \"amount\": 420.51484\n\n                },\n                {\n                    \"taxType\": \"T14\",\n                    \"amount\": 588.72078\n                },\n                {\n                    \"taxType\": \"T15\",\n                    \"amount\": 504.61781\n                },\n                {\n                    \"taxType\": \"T16\",\n                    \"amount\": 420.51484\n                },\n                {\n                    \"taxType\": \"T17\",\n                    \"amount\": 420.51484\n                },\n                {\n                    \"taxType\": \"T18\",\n                    \"amount\": 588.72078\n                },\n                {\n                    \"taxType\": \"T19\",\n                    \"amount\": 504.61781\n                },\n                {\n                    \"taxType\": \"T20\",\n                    \"amount\": 420.51484\n                }\n            ],\n            \"totalAmount\": 14082.88542,\n            \"extraDiscountAmount\": 5.00000,\n            \"totalItemsDiscountAmount\": 25.00000\n        }";
    }
}
